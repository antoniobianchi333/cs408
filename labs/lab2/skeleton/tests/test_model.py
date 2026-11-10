"""PurdueRCACModel: usage accounting, retries and request log (fake endpoint)."""
import json

import pytest
from minisweagent.exceptions import FormatError
from openai import APIError

from conftest import completion
from lab2.model import PurdueRCACModel, UsageUnavailableError, account


def model(url, tmp_path, **kwargs):
    return PurdueRCACModel(api_base=url, api_key_env="LAB2_TEST_KEY", usage_log_path=tmp_path / "requests.jsonl",
                           **kwargs)


@pytest.mark.parametrize("cached", [None, 0, 800])
def test_usage_is_counted_including_rejected_tool_calls(endpoint, tmp_path, cached):
    url, replies, requests = endpoint
    replies.extend([(200, completion('{"command":"true"}', cached)), (200, completion("{}", cached))])
    m = model(url, tmp_path)
    m.query([{"role": "user", "content": "test"}])
    with pytest.raises(FormatError):
        m.query([{"role": "user", "content": "test"}])
    summary = m.usage_summary()
    assert summary["input_tokens"] == 2000 and summary["output_tokens"] == 400
    assert summary["reasoning_tokens"] == 300
    assert summary["cached_input_tokens"] == (None if cached is None else 2 * cached)
    assert m.serialize()["info"]["model_stats"]["instance_cost"] is None
    assert all(r["stream"] is False and "max_tokens" not in r for r in requests)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["requests.jsonl"]


def test_missing_usage_stops_without_retries(endpoint, tmp_path):
    url, replies, requests = endpoint
    replies.append((200, completion('{"command":"true"}') | {"usage": None}))
    m = model(url, tmp_path)
    with pytest.raises(UsageUnavailableError):
        m.query([{"role": "user", "content": "test"}])
    assert len(requests) == 1 and m.usage_summary()["input_tokens"] is None
    rows = [json.loads(line) for line in (tmp_path / "requests.jsonl").read_text().splitlines()]
    assert rows[-1]["event"] == "response" and "accounting_error" in rows[-1]


@pytest.mark.parametrize("status,body", [
    (504, {"error": {"message": "gateway timeout", "type": "server_error"}}),
    (400, {"detail": "Rate limit exceeded. Please try again later."})])
def test_transient_failures_are_retried_and_logged(endpoint, tmp_path, status, body):
    url, replies, requests = endpoint
    replies.extend([(status, body), (200, completion('{"command":"true"}'))])
    m = model(url, tmp_path)
    m.query([{"role": "user", "content": "test"}])
    events = [json.loads(line)["event"] for line in (tmp_path / "requests.jsonl").read_text().splitlines()]
    assert len(requests) == 2 and events.count("request_failed") == 1 and events.count("response") == 1
    assert m.usage_summary()["input_tokens"] is None  # a failed attempt leaves the total unknown, never zero


def test_client_errors_are_not_retried(endpoint, tmp_path):
    url, replies, requests = endpoint
    replies.append((401, {"error": {"message": "bad key", "type": "auth"}}))
    with pytest.raises(APIError):
        model(url, tmp_path).query([{"role": "user", "content": "test"}])
    assert len(requests) == 1


def test_invalid_counts_and_streaming_are_rejected(endpoint, tmp_path):
    usage = completion("{}")["usage"]
    with pytest.raises(UsageUnavailableError):
        account(usage | {"total_tokens": 1199})
    with pytest.raises(UsageUnavailableError):
        account(usage | {"prompt_tokens_details": {"cached_tokens": 1001}})
    url, _, requests = endpoint
    with pytest.raises(ValueError, match="Streaming is disabled"):
        model(url, tmp_path, model_kwargs={"stream": True}).query([])
    assert not requests
