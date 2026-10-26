import json
import os
import threading
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
import yaml
from openai import APIError
from minisweagent.exceptions import FormatError
from lab2.__main__ import ROOT, run
from adapter.environment import UdockerEnvironment
from adapter.model import PurdueRCACModel, UsageUnavailableError, account
from adapter.skills import prepare_skills


@pytest.fixture
def endpoint(monkeypatch):
    monkeypatch.setenv('LAB2_TEST_KEY', 'test-only')
    replies, requests = deque(), []
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            requests.append(json.loads(self.rfile.read(int(self.headers['Content-Length']))))
            status, reply = replies.popleft()
            body = json.dumps(reply).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}/api', replies, requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def completion(arguments, cached=None):
    return {'id': 'test-response', 'object': 'chat.completion', 'created': 0, 'model': 'qwen3.8:27b',
            'choices': [{'index': 0, 'finish_reason': 'tool_calls', 'message': {'role': 'assistant',
                'content': '', 'tool_calls': [{'id': 'call-1', 'type': 'function',
                    'function': {'name': 'bash', 'arguments': arguments}}]}}],
            'usage': {'prompt_tokens': 1000, 'completion_tokens': 200, 'total_tokens': 1200,
                'completion_tokens_details': {'reasoning_tokens': 150},
                'prompt_tokens_details': None if cached is None else {'cached_tokens': cached}}}


@pytest.mark.parametrize('cached', [None, 0, 800])
def test_sdk_reports_real_usage_including_rejected_tool_calls(endpoint, tmp_path, cached):
    url, replies, requests = endpoint
    replies.extend([(200, completion('{"command":"true"}', cached)), (200, completion('{}', cached))])
    model = PurdueRCACModel(api_base=url, api_key_env='LAB2_TEST_KEY', usage_log_path=tmp_path/'requests.jsonl')
    model.query([{'role': 'user', 'content': 'test'}])
    with pytest.raises(FormatError):
        model.query([{'role': 'user', 'content': 'test'}])
    summary = model.usage_summary()
    assert summary['input_tokens'] == 2000 and summary['output_tokens'] == 400
    assert summary['reasoning_tokens'] == 300
    assert summary['cached_input_tokens'] == (None if cached is None else 2 * cached)
    assert model.serialize()['info']['model_stats']['instance_cost'] is None
    assert all(r['stream'] is False and 'max_tokens' not in r for r in requests)
    assert len(list((tmp_path/'raw-model-responses').glob('*.json'))) == 2


@pytest.mark.parametrize('gateway_error', [False, True])
def test_missing_usage_or_gateway_failure_stops_without_untracked_retries(endpoint, tmp_path, gateway_error):
    url, replies, requests = endpoint
    reply = completion('{"command":"true"}') | {'usage': None}
    replies.append((504, {'error': {'message': 'gateway timeout', 'type': 'server_error'}}) if gateway_error else (200, reply))
    model = PurdueRCACModel(api_base=url, api_key_env='LAB2_TEST_KEY', usage_log_path=tmp_path/'requests.jsonl')
    with pytest.raises(APIError if gateway_error else UsageUnavailableError):
        model.query([{'role': 'user', 'content': 'test'}])
    assert len(requests) == 1 and model.usage_summary()['input_tokens'] is None
    assert not model.usage_summary()['token_usage_complete']
    assert (tmp_path/'requests.jsonl').exists()


def test_invalid_token_counts_and_streaming_are_rejected(endpoint):
    data = completion('{}')['usage']
    with pytest.raises(UsageUnavailableError):
        account(data | {'total_tokens': 1199})
    with pytest.raises(UsageUnavailableError):
        account(data | {'prompt_tokens_details': {'cached_tokens': 1001}})
    url, _, requests = endpoint
    with pytest.raises(ValueError, match='Streaming is disabled'):
        PurdueRCACModel(api_base=url, api_key_env='LAB2_TEST_KEY', model_kwargs={'stream': True}).query([])
    assert not requests


@pytest.mark.parametrize('change_production', [False, True])
@pytest.mark.parametrize('with_skills', [False, True])
def test_official_agent_local_runner_lazy_skills_and_source_integrity(endpoint, tmp_path, change_production, with_skills):
    task = tmp_path/'task'
    (task/'project').mkdir(parents=True)
    (task/'project/app.py').write_text('VALUE = 1\n')
    spec = {'type': 'TW', 'language': 'python', 'prompt': 'prompt.md', 'project': 'project',
            'test_paths': ['.'], 'environment': {'environment_class': 'minisweagent.environments.local.LocalEnvironment'}}
    (task/'task.yaml').write_text(yaml.safe_dump(spec))
    (task/'prompt.md').write_text('Write tests for app.VALUE.\n')
    skill = tmp_path/'skill'
    (skill/'references').mkdir(parents=True)
    (skill/'skill.yaml').write_text(yaml.safe_dump({'name': 'probe', 'description': 'Generic loader fixture.',
        'instructions': 'Read references/probe.txt only when needed.'}))
    (skill/'references/probe.txt').write_text('Supplementary loader fixture.\n')
    selection = tmp_path/'skills.yaml'
    selection.write_text('skills:\n  enabled: [skill]\n')
    command = "printf 'from app import VALUE\ndef test_value():\n    assert VALUE == 1\n' > test_probe.py"
    if change_production:
        command += "\nprintf 'VALUE = 2\\n' > app.py"
    config = yaml.safe_load((ROOT/'config.yaml').read_text())
    url, replies, requests = endpoint
    commands = ['cat .skills/probe/skill.yaml .skills/probe/references/probe.txt' if with_skills else 'pwd', command,
                'echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT']
    replies.extend((200, completion(json.dumps({'command': c}))) for c in commands)
    config['model'] |= {'api_base': url, 'api_key_env': 'LAB2_TEST_KEY'}
    out = tmp_path/'out'
    result = run(task, config, out, selection if with_skills else None)
    trajectory = json.loads((out/'trajectory.json').read_text())
    if with_skills:
        assert 'probe: Generic loader fixture.' in trajectory['messages'][0]['content']
        assert 'Read references/probe.txt only when needed.' not in trajectory['messages'][0]['content']
        assert any('Supplementary loader fixture.' in str(m.get('content', '')) for m in trajectory['messages'][2:])
    else:
        assert result['skills'] == [] and 'Available skills' not in trajectory['messages'][0]['content']
        assert not (out/'skills').exists() and not (out/'work/.skills').exists()
    assert (out/'submission/test_probe.py').is_file()
    assert result['usage']['input_tokens'] == 3000 and result['usage']['output_tokens'] == 600
    assert trajectory['info']['model_stats']['instance_cost'] is None
    assert result['valid_submission'] is not change_production
    assert result['unexpected_changes'] == (['app.py'] if change_production else [])
    assert (task/'project/app.py').read_text() == 'VALUE = 1\n'
    with pytest.raises(FileExistsError):
        run(task, config, out)


def test_empty_selection_and_duplicate_names(tmp_path):
    selected = tmp_path/'skills.yaml'
    selected.write_text('skills:\n  enabled: []\n')
    assert prepare_skills(selected, tmp_path/'empty') == ('', [])
    assert not (tmp_path/'empty').exists()
    for name in ['first', 'second']:
        (tmp_path/name).mkdir()
        (tmp_path/name/'skill.yaml').write_text('name: duplicate\ndescription: fixture\ninstructions: fixture\n')
    selected.write_text('skills:\n  enabled: [first, second]\n')
    with pytest.raises(ValueError, match='Duplicate'):
        prepare_skills(selected, tmp_path/'copy')
    assert not (tmp_path/'copy').exists()


@pytest.mark.skipif(not (os.getenv('LAB2_TEST_IMAGE_STORE') and os.getenv('LAB2_TEST_IMAGE')),
                    reason='Set both variables to exercise an existing local udocker image')
def test_real_udocker_persistence_mount_timeout_and_cleanup(tmp_path):
    store = Path(os.environ['LAB2_TEST_IMAGE_STORE'])
    (tmp_path/'selected').mkdir()
    (tmp_path/'selected/probe.txt').write_text('mounted fixture\n')
    env = UdockerEnvironment(image=os.environ['LAB2_TEST_IMAGE'], repos=store/'repos', layers=store/'layers',
        containers=tmp_path/'containers', volumes={str(tmp_path/'selected'): '/app/.skills'})
    root = env.root
    try:
        assert 'mounted fixture' in env.execute({'command': 'cat .skills/probe.txt'})['output']
        assert env.execute({'command': 'echo persistent > /tmp/lab2-probe'})['returncode'] == 0
        assert 'persistent' in env.execute({'command': 'cat /tmp/lab2-probe'})['output']
        assert env.execute({'command': 'sleep 10 & wait'}, timeout=1)['returncode'] == 124
        assert env.execute({'command': 'true'})['returncode'] == 0
    finally:
        env.cleanup()
    assert not root.exists() and not (tmp_path/'containers'/env.name).exists()
