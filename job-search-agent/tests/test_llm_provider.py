"""
tests/test_llm_provider.py
-----------------------------
Tests for integrations/llm/anthropic_provider.py.

None of these tests make a real network call or need a real API key -
they construct the provider with a fake key (which only matters once you
actually call the API) and replace `self._client.messages.create` with a
mock that raises/returns whatever we want to test. This lets us verify
our error-mapping and retry logic exhaustively without spending money or
depending on the Anthropic API being reachable.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import httpx
import pytest
from anthropic import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    RateLimitError,
)
from pydantic import BaseModel

from config.settings import settings
from integrations.llm.anthropic_provider import AnthropicLLMProvider
from integrations.llm.base import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMResponseError,
    LLMTimeoutError,
)


class DummyOutput(BaseModel):
    foo: str


def make_provider(max_retries: int = 1) -> AnthropicLLMProvider:
    """A provider with a fake key - fine, because we never let it make a
    real network call in these tests."""
    return AnthropicLLMProvider(api_key="sk-ant-fake-key-for-tests", max_retries=max_retries)


def _fake_request() -> httpx.Request:
    return httpx.Request("POST", "https://api.anthropic.com/v1/messages")


def _fake_response(status_code: int) -> httpx.Response:
    return httpx.Response(status_code, request=_fake_request())


def _fake_tool_use_response(input_dict: dict):
    """Build a fake Anthropic response with one tool_use content block,
    shaped like the real SDK's response enough for our code to read it."""
    block = SimpleNamespace(type="tool_use", id="toolu_123", input=input_dict)
    return SimpleNamespace(
        content=[block],
        usage=SimpleNamespace(input_tokens=100, output_tokens=20),
    )


def test_missing_api_key_raises_authentication_error(monkeypatch):
    # `settings` is a module-level singleton created once, at import time,
    # from your real .env file -- so once you have a real ANTHROPIC_API_KEY
    # in .env, monkeypatch.delenv("ANTHROPIC_API_KEY") alone doesn't blank
    # it out (that only clears the OS environment variable, not the value
    # `settings` already read from .env before this test ever ran). We
    # patch the already-loaded settings object directly instead, which is
    # the actual fallback AnthropicLLMProvider reads from.
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(settings, "anthropic_api_key", "")
    with pytest.raises(LLMAuthenticationError):
        AnthropicLLMProvider(api_key="")


def test_successful_structured_output_parses_first_try():
    provider = make_provider()
    provider._client.messages.create = MagicMock(
        return_value=_fake_tool_use_response({"foo": "bar"})
    )
    result = provider.complete_structured("system", "user", DummyOutput)
    assert result == DummyOutput(foo="bar")
    provider._client.messages.create.assert_called_once()


def test_invalid_schema_retries_once_then_succeeds():
    provider = make_provider()
    responses = [
        _fake_tool_use_response({"wrong_field": "oops"}),  # fails validation
        _fake_tool_use_response({"foo": "corrected"}),  # succeeds on retry
    ]
    provider._client.messages.create = MagicMock(side_effect=responses)
    result = provider.complete_structured("system", "user", DummyOutput)
    assert result == DummyOutput(foo="corrected")
    assert provider._client.messages.create.call_count == 2


def test_invalid_schema_twice_raises_llm_response_error():
    provider = make_provider()
    provider._client.messages.create = MagicMock(
        return_value=_fake_tool_use_response({"wrong_field": "oops"})
    )
    with pytest.raises(LLMResponseError):
        provider.complete_structured("system", "user", DummyOutput)


def test_authentication_error_is_not_retried_and_maps_correctly():
    provider = make_provider(max_retries=3)
    provider._client.messages.create = MagicMock(
        side_effect=AuthenticationError(
            "invalid key", response=_fake_response(401), body=None
        )
    )
    with pytest.raises(LLMAuthenticationError):
        provider.complete_structured("system", "user", DummyOutput)
    # Should fail fast - no retries for a bad API key.
    provider._client.messages.create.assert_called_once()


def test_rate_limit_error_maps_to_llm_rate_limit_error():
    provider = make_provider(max_retries=1)  # keep the test fast - no real sleeping
    provider._client.messages.create = MagicMock(
        side_effect=RateLimitError("rate limited", response=_fake_response(429), body=None)
    )
    with pytest.raises(LLMRateLimitError):
        provider.complete_structured("system", "user", DummyOutput)


def test_timeout_error_maps_to_llm_timeout_error():
    provider = make_provider(max_retries=1)
    provider._client.messages.create = MagicMock(
        side_effect=APITimeoutError(request=_fake_request())
    )
    with pytest.raises(LLMTimeoutError):
        provider.complete_structured("system", "user", DummyOutput)


def test_connection_error_maps_to_llm_connection_error():
    provider = make_provider(max_retries=1)
    provider._client.messages.create = MagicMock(
        side_effect=APIConnectionError(message="no network", request=_fake_request())
    )
    with pytest.raises(LLMConnectionError):
        provider.complete_structured("system", "user", DummyOutput)


def test_bad_request_error_maps_to_llm_response_error_and_is_not_retried():
    provider = make_provider(max_retries=3)
    provider._client.messages.create = MagicMock(
        side_effect=BadRequestError("bad request", response=_fake_response(400), body=None)
    )
    with pytest.raises(LLMResponseError):
        provider.complete_structured("system", "user", DummyOutput)
    provider._client.messages.create.assert_called_once()
