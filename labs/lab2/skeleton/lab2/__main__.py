"""Run a course task with the official agent and collect changed test files."""
import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml
from minisweagent.agents.default import DefaultAgent
from minisweagent.environments import get_environment
from minisweagent.models import get_model
from adapter.skills import prepare_skills

ROOT = Path(__file__).resolve().parents[1]


def git(work: Path, *args: str) -> str:
    return subprocess.check_output(['git', '-C', str(work), *args], text=True).strip()


def snapshot(work: Path) -> dict:
    names = git(work, 'ls-files', '--cached', '--others', '--exclude-standard', '-z').split('\0')
    return {name: ('link:' + str(p.readlink()) if p.is_symlink() else hashlib.sha256(p.read_bytes()).hexdigest())
            for name in names if name and not name.startswith('.skills/')
            and (p := work/name).exists()}


def collect(work: Path, before: dict, head: str, spec: dict, out: Path) -> dict:
    after = snapshot(work)
    changed = {name for name in before.keys() | after.keys() if before.get(name) != after.get(name)}
    tests = {name for name in changed if name in after and not (work/name).is_symlink()
             and any(Path(name).is_relative_to(p) for p in spec['test_paths'])
             and (Path(name).match('*_test.go') if spec['language'] == 'go'
                  else Path(name).match('test_*.py') or Path(name).match('*_test.py'))
             and (name not in before or name in spec.get('editable', []))}
    unexpected = sorted(changed - tests)
    if git(work, 'rev-parse', 'HEAD') != head:
        unexpected.append('.git/HEAD')
    for name in sorted(tests):
        target = out/'submission'/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(work/name, target)
    return {'files': sorted(tests), 'unexpected_changes': unexpected}


def run(task: Path, config: dict, out: Path, skills: Path | None = None,
        image_store: Path | None = None) -> dict:
    spec = yaml.safe_load((task/'task.yaml').read_text())
    if spec.get('architecture') and platform.machine().lower() not in {spec['architecture'], 'arm64'}:
        raise ValueError(f"This task image requires {spec['architecture']}; host is {platform.machine()}")
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    catalog, selected = prepare_skills(skills, out/'skills')
    (out/'skills-index.txt').write_text(catalog)
    environment = config.get('environment', {}) | spec['environment']
    if spec.get('project'):
        work = out/'work'
        shutil.copytree(task/spec['project'], work)
        git(work, 'init', '-q')
        (work/'.git/info/exclude').write_text('.skills/\n__pycache__/\n.pytest_cache/\n')
        git(work, 'add', '.')
        git(work, '-c', 'user.name=CS408', '-c', 'user.email=cs408@localhost', 'commit', '-qm', 'Task baseline')
        environment['cwd'] = str(work)
        environment['env'] = environment.get('env', {}) | {
            'PATH': str(Path(sys.executable).parent) + os.pathsep + os.environ.get('PATH', ''),
            'PYTHONDONTWRITEBYTECODE': '1', config['model'].get('api_key_env', 'PURDUE_RCAC_API_KEY'): ''}
        if selected:
            shutil.copytree(out/'skills', work/'.skills')
    else:
        store = (image_store or ROOT/'.cache/udocker').resolve()
        environment |= {name: str(store/name) for name in ['repos', 'layers', 'containers']}
        if selected:
            environment['volumes'] = environment.get('volumes', {}) | {str(out/'skills'): '/app/.skills'}
    model_config = config['model'] | {'usage_log_path': str(out/'model-requests.jsonl')}
    agent_config = config['agent'] | {'output_path': str(out/'trajectory.json')}
    (out/'config.yaml').write_text(yaml.safe_dump({'model': model_config, 'agent': agent_config, 'environment': environment}))
    (out/'task.yaml').write_text(yaml.safe_dump(spec))
    prompt = (task/spec['prompt']).read_text() + '\nAllowed test directories: ' + ', '.join(spec['test_paths'])
    (out/'prompt.md').write_text(prompt)
    result = {'task': task.name, 'type': spec['type'], 'skills': selected, 'valid_submission': False}
    started, agent_started = time.monotonic(), None
    env = model = agent = before = None
    try:
        env = get_environment(environment)
        if not spec.get('project'):
            work = env.root/'app'
        if spec.get('prepare'):
            prepared = env.execute({'command': spec['prepare']}, timeout=600)
            (out/'prepare.log').write_text(prepared['output'])
            if prepared['returncode']:
                raise RuntimeError('Image preparation failed; see prepare.log')
        before, head = snapshot(work), git(work, 'rev-parse', 'HEAD')
        model = get_model(config=model_config)
        agent = DefaultAgent(model, env, **agent_config)
        agent_started = time.monotonic()
        result['agent_exit'] = agent.run(prompt, skills_catalog=catalog)
    finally:
        error = sys.exc_info()[1]
        result['error'] = None if error is None else f'{type(error).__name__}: {error}'
        try:
            if before is not None:
                result.update(collect(work, before, head, spec, out))
                result['valid_submission'] = (error is None and bool(result['files'])
                    and not result['unexpected_changes'] and result.get('agent_exit', {}).get('exit_status') == 'Submitted')
        finally:
            result['agent_seconds'] = None if agent_started is None else round(time.monotonic() - agent_started, 2)
            result['elapsed_seconds'] = round(time.monotonic() - started, 2)
            result['model_calls'] = getattr(agent, 'n_calls', 0)
            result['usage'] = model.usage_summary() if hasattr(model, 'usage_summary') else None
            (out/'result.json').write_text(json.dumps(result, indent=2) + '\n')
            getattr(env, 'cleanup', lambda: None)()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    tasks = {str(p.parent.relative_to(ROOT/'tasks')): p.parent for p in (ROOT/'tasks').rglob('task.yaml')}
    parser.add_argument('task', choices=sorted(tasks))
    parser.add_argument('--config', type=Path, default=ROOT/'config.yaml')
    parser.add_argument('--skills-config', type=Path,
                        help='Skill list YAML, e.g. skillsets/example.yaml; omit for vanilla')
    parser.add_argument('--output', type=Path, help='New output directory; never overwrite a run')
    parser.add_argument('--image-store', type=Path, help='udocker store; defaults to .cache/udocker')
    args = parser.parse_args()
    out = args.output or ROOT/'outputs'/args.task/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')
    result = run(tasks[args.task], yaml.safe_load(args.config.read_text()), out, args.skills_config, args.image_store)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['valid_submission'] else 1)


if __name__ == '__main__':
    main()
