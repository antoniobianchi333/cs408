"""PurdueRCACModel: the course model class for mini-swe-agent (config.yaml model_class).

Calls the Purdue RCAC GenAI Chat Completions API with the OpenAI SDK, keeps
mini-swe-agent's tool parsing, and appends one JSON row per request attempt
(started, failed or answered, with token usage) to `usage_log_path`
(jobs/<alias>/<id>/model-requests.jsonl). Token counts are never invented: a
response without valid usage stops the run.

Retries: mini-swe-agent retries every exception not in `abort_exceptions`
(MSWEA_MODEL_RETRY_STOP_AFTER_ATTEMPT, default 10 attempts, 4-60 s backoff):
timeouts, connection errors, 5xx, 429 and Purdue's HTTP 400 "Rate limit
exceeded", which is re-raised as TransientAPIError so it is not aborted.

hide_process_environment() keeps the API key out of reach of the agent's
commands, which run as the same user (see lab2.agent and lab2.run).
"""
import ctypes
import json
import os
import sys
import time
from pathlib import Path

from minisweagent.models.litellm_model import LitellmModel, LitellmModelConfig
from minisweagent.models.utils.actions_toolcall import BASH_TOOL
from openai import (APIResponseValidationError, AuthenticationError, BadRequestError, ConflictError,
                    NotFoundError, OpenAI, PermissionDeniedError, UnprocessableEntityError)


PR_SET_DUMPABLE = 4  # linux/prctl.h


def hide_process_environment() -> None:
    """Make this process non-dumpable (Linux), so same-user processes cannot read its /proc/<pid>/environ.

    The API key is in the environment of the lab2 and Harbor processes; agent
    commands (host processes for the warmup; udocker containers see the host's
    /proc too) run as the same user and could otherwise read it from there.
    Children are unaffected: execve makes them dumpable again.
    """
    if sys.platform.startswith("linux") and ctypes.CDLL(None, use_errno=True).prctl(PR_SET_DUMPABLE, 0, 0, 0, 0):
        raise OSError(ctypes.get_errno(), "prctl(PR_SET_DUMPABLE, 0) failed")


class TransientAPIError(RuntimeError):
    """A retryable provider failure that the SDK reports as a client error."""


class UsageUnavailableError(RuntimeError):
    """A response without valid token usage."""


def _count(value, name):
    if type(value) is not int or value < 0:
        raise UsageUnavailableError(f"Missing or invalid {name}: {value!r}")
    return value


def account(usage) -> dict:
    """Validated token counts of one response's `usage` object."""
    if not isinstance(usage, dict):
        raise UsageUnavailableError("Response has no usage object")
    prompt = _count(usage.get("prompt_tokens"), "prompt_tokens")
    output = _count(usage.get("completion_tokens"), "completion_tokens")
    total = _count(usage.get("total_tokens"), "total_tokens")
    if total != prompt + output:
        raise UsageUnavailableError("total_tokens does not equal input plus output")
    cached = (usage.get("prompt_tokens_details") or {}).get("cached_tokens")
    if cached is not None and _count(cached, "cached_tokens") > prompt:
        raise UsageUnavailableError("cached_tokens exceeds prompt_tokens")
    reasoning = (usage.get("completion_tokens_details") or {}).get("reasoning_tokens")
    if reasoning is not None and _count(reasoning, "reasoning_tokens") > output:
        raise UsageUnavailableError("reasoning_tokens exceeds completion_tokens")
    return {"input_tokens": prompt, "output_tokens": output, "total_tokens": total,
            "reasoning_tokens": reasoning, "cached_input_tokens": cached}


def summarize(records: list[dict], request_count: int) -> dict:
    """Run totals; a total is None unless every request attempt reported usage."""
    valid = [r["accounting"] for r in records if r.get("event") == "response" and r.get("accounting")]
    complete = len(valid) == request_count

    def total(key):
        values = [r[key] for r in valid]
        return sum(values) if complete and None not in values else None

    return {"request_attempts": request_count, "responses_with_valid_usage": len(valid),
            "token_usage_complete": complete,
            "input_tokens": total("input_tokens"), "output_tokens": total("output_tokens"),
            "reasoning_tokens": total("reasoning_tokens"), "cached_input_tokens": total("cached_input_tokens"),
            "known_input_tokens": sum(r["input_tokens"] for r in valid),
            "known_output_tokens": sum(r["output_tokens"] for r in valid)}


class PurdueRCACConfig(LitellmModelConfig):
    model_name: str = "openai/qwen3.8:27b"
    api_base: str = "https://genai.rcac.purdue.edu/api"
    api_key_env: str = "PURDUE_RCAC_API_KEY"
    cost_tracking: str = "default"
    usage_log_path: Path | None = None


class PurdueRCACModel(LitellmModel):
    abort_exceptions = [AuthenticationError, PermissionDeniedError, NotFoundError, BadRequestError, ConflictError,
                        UnprocessableEntityError, APIResponseValidationError, UsageUnavailableError, ValueError,
                        KeyboardInterrupt]

    def __init__(self, **kwargs):
        super().__init__(config_class=PurdueRCACConfig, **kwargs)
        self.request_count = 0
        self.usage_records = []
        if not os.environ.get(self.config.api_key_env):
            raise ValueError(f"Set {self.config.api_key_env} in the host environment")
        if any(key in self.config.model_kwargs for key in ("api_key", "api_base")):
            raise ValueError("Use api_base and api_key_env fields, not credentials in model_kwargs")
        if self.config.usage_log_path:
            Path(self.config.usage_log_path).parent.mkdir(parents=True, exist_ok=True)
        self.client = OpenAI(api_key=os.environ[self.config.api_key_env], base_url=self.config.api_base, max_retries=0)

    def _query(self, messages, **kwargs):
        options = self.config.model_kwargs | kwargs
        options.pop("num_retries", None)
        # Every completed response must carry its usage, which streaming would drop.
        if options.pop("stream", False) or "stream_options" in options:
            raise ValueError("Streaming is disabled: every completed response must retain token usage")
        self.request_count += 1
        started = time.time()
        identity = {"request_number": self.request_count, "started_at": started}
        self._record(identity | {"event": "request_started"})
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name.removeprefix("openai/"), messages=messages,
                tools=[BASH_TOOL], stream=False, **options)
        except BaseException as error:
            self._record(identity | {"event": "request_failed", "elapsed_seconds": time.time() - started,
                                     "error_type": type(error).__name__,
                                     "http_status": getattr(error, "status_code", None),
                                     "request_id": getattr(error, "request_id", None)})
            if isinstance(error, BadRequestError) and "rate limit" in str(error).lower():
                raise TransientAPIError(str(error)) from error
            raise
        usage = response.model_dump(mode="json").get("usage")
        row = identity | {"event": "response", "response_id": response.id,
                          "elapsed_seconds": time.time() - started, "usage": usage, "accounting": None}
        try:
            row["accounting"] = account(usage)
            if not response.choices:
                raise UsageUnavailableError("Purdue returned no choices")
        except UsageUnavailableError as error:
            row["accounting_error"] = str(error)
            raise
        finally:
            self._record(row)
        return response

    def _calculate_cost(self, response):
        usage = account(response.usage.model_dump(mode="json") if response.usage else None)
        # mini-swe-agent requires a numeric cost; there is no price for this API.
        return {"cost": 0.0, "usage_accounting": usage, "cost_tracking": "disabled_by_user"}

    def _record(self, row):
        self.usage_records.append(row)
        if self.config.usage_log_path:
            with Path(self.config.usage_log_path).open("a") as file:
                file.write(json.dumps(row) + "\n")

    def usage_summary(self) -> dict:
        return summarize(self.usage_records, self.request_count)

    def serialize(self):
        data = super().serialize()
        data["info"]["usage_accounting"] = self.usage_summary()
        data["info"]["model_stats"] = {"instance_cost": None}
        data["info"]["cost_tracking"] = "disabled_by_user"
        return data
