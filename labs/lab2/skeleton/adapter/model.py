"""Purdue RCAC Chat Completions model using upstream tool parsing and formatting."""
import hashlib
import json
import os
import time
from pathlib import Path

from openai import OpenAI, APIError
from minisweagent.models.litellm_model import LitellmModel, LitellmModelConfig
from minisweagent.models.utils.actions_toolcall import BASH_TOOL

class UsageUnavailableError(RuntimeError):
    """Never substitute zero token counts for missing usage."""


def _count(value, name):
    if type(value) is not int or value < 0:
        raise UsageUnavailableError(f"Missing or invalid {name}: {value!r}")
    return value


def account(usage):
    if not isinstance(usage, dict):
        raise UsageUnavailableError("Response has no usage object")
    prompt = _count(usage.get('prompt_tokens'), 'prompt_tokens')
    output = _count(usage.get('completion_tokens'), 'completion_tokens')
    total = _count(usage.get('total_tokens'), 'total_tokens')
    if total != prompt + output:
        raise UsageUnavailableError('total_tokens does not equal input plus output')
    details = usage.get('prompt_tokens_details') or {}
    cached = details.get('cached_tokens')
    if cached is not None:
        cached = _count(cached, 'cached_tokens')
        if cached > prompt:
            raise UsageUnavailableError('cached_tokens exceeds prompt_tokens')
    reasoning = (usage.get('completion_tokens_details') or {}).get('reasoning_tokens')
    if reasoning is not None:
        reasoning = _count(reasoning, 'reasoning_tokens')
        if reasoning > output:
            raise UsageUnavailableError('reasoning_tokens exceeds completion_tokens')
    return {
        'input_tokens': prompt, 'output_tokens': output, 'total_tokens': total,
        'reasoning_tokens': reasoning, 'cached_input_tokens': cached,
        'uncached_input_tokens': None if cached is None else prompt - cached,
        'cache_hit_ratio': None if cached is None or prompt == 0 else cached / prompt,
        'cache_usage_status': 'not_reported' if cached is None else 'provider_reported',
    }


def summarize(records, request_count):
    completed = [r for r in records if r.get('event') == 'response']
    valid = [r['accounting'] for r in completed if r.get('accounting') is not None]
    complete = len(valid) == request_count
    cache_complete = complete and all(r['cached_input_tokens'] is not None for r in valid)
    known_cached = sum(r['cached_input_tokens'] for r in valid if r['cached_input_tokens'] is not None)
    tokens = sum(r['input_tokens'] for r in valid)
    return {
        'request_attempts': request_count, 'responses_with_valid_usage': len(valid),
        'token_usage_complete': complete,
        'input_tokens': tokens if complete else None,
        'output_tokens': sum(r['output_tokens'] for r in valid) if complete else None,
        'known_input_tokens': tokens,
        'known_output_tokens': sum(r['output_tokens'] for r in valid),
        'reasoning_tokens': sum(r['reasoning_tokens'] for r in valid)
                            if complete and all(r['reasoning_tokens'] is not None for r in valid) else None,
        'cache_usage_complete': cache_complete,
        'cached_input_tokens': known_cached if cache_complete else None,
        'cache_hit_ratio': known_cached / tokens if cache_complete and tokens else None,
    }


class PurdueRCACConfig(LitellmModelConfig):
    model_name: str = "openai/qwen3.8:27b"
    api_base: str = "https://genai.rcac.purdue.edu/api"
    api_key_env: str = "PURDUE_RCAC_API_KEY"
    cost_tracking: str = "default"
    usage_log_path: Path | None = None


class PurdueRCACModel(LitellmModel):
    abort_exceptions = [APIError, UsageUnavailableError, ValueError, KeyboardInterrupt]

    def __init__(self, **kwargs):
        super().__init__(config_class=PurdueRCACConfig, **kwargs)
        self.request_count = 0
        self.usage_records = []
        if self.config.usage_log_path:
            self.config.usage_log_path.parent.mkdir(parents=True, exist_ok=True)
        if not os.environ.get(self.config.api_key_env):
            raise ValueError(f"Set {self.config.api_key_env} in the host environment")
        if any(key in self.config.model_kwargs for key in ("api_key", "api_base")):
            raise ValueError("Use api_base and api_key_env fields, not credentials in model_kwargs")
        self.client = OpenAI(api_key=os.environ[self.config.api_key_env], base_url=self.config.api_base, max_retries=0)

    def _query(self, messages, **kwargs):
        options = self.config.model_kwargs | kwargs
        options.pop('num_retries', None)
        if options.pop('stream', False):
            raise ValueError('Streaming is disabled: every completed response must retain token usage')
        if 'stream_options' in options:
            raise ValueError('stream_options is invalid for non-streaming accounting runs')
        self.request_count += 1
        started = time.time()
        request = {'model': self.config.model_name.removeprefix('openai/'),
                   'messages': messages, 'tools': [BASH_TOOL], 'stream': False}
        identity = {'request_number': self.request_count, 'started_at': started,
                    'request_sha256': hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()}
        self._record(identity | {'event': 'request_started'})
        try:
            response = self.client.chat.completions.create(**request, **options)
        except BaseException as error:
            self._record(identity | {'event': 'request_failed', 'elapsed_seconds': time.time()-started,
                                    'error_type': type(error).__name__,
                                    'http_status': getattr(error, 'status_code', None),
                                    'request_id': getattr(error, 'request_id', None)})
            raise
        raw = response.model_dump(mode='json')
        # Persist before cost validation or tool parsing, including malformed tool calls.
        if self.config.usage_log_path:
            directory = self.config.usage_log_path.parent/'raw-model-responses'
            directory.mkdir(exist_ok=True)
            (directory/f'{self.request_count:04d}.json').write_text(json.dumps(raw, indent=2)+'\n')
        row = identity | {'event': 'response', 'response_id': response.id,
                          'elapsed_seconds': time.time()-started, 'usage': raw.get('usage'),
                          'accounting': None}
        try:
            row['accounting'] = account(raw.get('usage'))
            if not response.choices:
                raise UsageUnavailableError('Purdue returned no choices')
        except (UsageUnavailableError, ValueError) as error:
            row['accounting_error'] = str(error)
            self._record(row)
            raise
        self._record(row)
        return response

    def _calculate_cost(self, response):
        usage = account(response.usage.model_dump(mode='json') if response.usage else None)
        # The official agent requires a numeric internal counter. This is not a price.
        return {'cost': 0.0, 'usage_accounting': usage, 'cost_tracking': 'disabled_by_user'}

    def _record(self, row):
        self.usage_records.append(row)
        if self.config.usage_log_path:
            with self.config.usage_log_path.open('a') as file:
                file.write(json.dumps(row)+'\n')
                file.flush()
            target = self.config.usage_log_path.parent/'usage-summary.json'
            temporary = target.with_suffix('.tmp')
            temporary.write_text(json.dumps(self.usage_summary(), indent=2)+'\n')
            temporary.replace(target)

    def usage_summary(self):
        return summarize(self.usage_records, self.request_count)

    def serialize(self):
        data = super().serialize()
        data['info']['usage_accounting'] = self.usage_summary()
        data['info']['model_stats'] = {'instance_cost': None}
        data['info']['cost_tracking'] = 'disabled_by_user'
        return data
