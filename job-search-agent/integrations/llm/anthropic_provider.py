"""
integrations/llm/anthropic_provider.py
----------------------------------------
The Anthropic (Claude) implementation of the `LLMProvider` interface
defined in `base.py`. This is the ONLY file in the project that imports
the `anthropic` package.

HOW STRUCTURED OUTPUT WORKS HERE (read this before the code):
Claude doesn't have a simple "give me back JSON" switch. Instead, we use
"tool use": we describe a fake tool whose *input schema* is exactly the
shape of the Pydantic model we want back (built automatically from
`output_model.model_json_schema()`), and we force Claude to call that
tool (`tool_choice`) instead of replying with plain text. Claude then
replies with a `tool_use` block whose `.input` is a dict that already
matches our schema's field names and types. We validate that dict with
Pydantic (`output_model.model_validate(...)`) before trusting it. If it
doesn't validate (rare, but possible), we send one corrective follow-up
message telling Claude exactly what was wrong and asking it to call the
tool again — and only give up after that.
"""

import time
from typing import TypeVar

import anthropic
from pydantic import BaseModel, ValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from config.logging_setup import get_logger
from config.settings import settings
from integrations.llm.base import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMProvider,
    LLMRateLimitError,
    LLMResponseError,
    LLMTimeoutError,
)

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)

# Anthropic errors that are worth retrying (transient / "try again later").
_RETRYABLE_ANTHROPIC_ERRORS = (
    anthropic.APITimeoutError,
    anthropic.APIConnectionError,
    anthropic.RateLimitError,
    anthropic.InternalServerError,  # Anthropic-side 5xx
)


class AnthropicLLMProvider(LLMProvider):
    """LLMProvider implementation backed by the Anthropic Messages API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        max_output_tokens: int | None = None,
        timeout_seconds: float | None = None,
        max_retries: int | None = None,
    ):
        api_key = api_key or settings.anthropic_api_key
        if not api_key:
            raise LLMAuthenticationError(
                "No ANTHROPIC_API_KEY found. Copy .env.example to .env and set "
                "ANTHROPIC_API_KEY to your real key from https://console.anthropic.com/"
            )

        self.model = model or settings.llm_model
        self.max_output_tokens = max_output_tokens or settings.llm_max_output_tokens
        self.max_retries = max_retries or settings.llm_max_retries
        timeout_seconds = timeout_seconds or settings.llm_timeout_seconds

        # The SDK client itself gets a timeout so a hung connection doesn't
        # block forever; our own retry loop (below) handles trying again.
        self._client = anthropic.Anthropic(api_key=api_key, timeout=timeout_seconds)

    def complete_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        output_model: type[T],
    ) -> T:
        tool_name = f"return_{output_model.__name__.lower()}"
        tool_schema = {
            "name": tool_name,
            "description": f"Return the analysis as {output_model.__name__}.",
            "input_schema": output_model.model_json_schema(),
        }

        messages: list[dict] = [{"role": "user", "content": user_prompt}]

        # Up to 2 total tries: 1 normal call + 1 corrective retry if the
        # first response doesn't validate against our schema.
        last_error: Exception | None = None
        for attempt in range(2):
            raw_response = self._call_with_retry(system_prompt, messages, tool_schema)
            tool_use_block = next(
                (b for b in raw_response.content if b.type == "tool_use"), None
            )
            if tool_use_block is None:
                last_error = LLMResponseError(
                    "Claude did not call the expected tool at all — got: "
                    f"{[b.type for b in raw_response.content]}"
                )
                break

            try:
                return output_model.model_validate(tool_use_block.input)
            except ValidationError as e:
                logger.warning(
                    "LLM structured output failed validation (attempt %d): %s",
                    attempt + 1,
                    e,
                )
                last_error = e
                if attempt == 0:
                    # Give Claude one chance to correct itself.
                    messages.append(
                        {"role": "assistant", "content": raw_response.content}
                    )
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_use_block.id,
                                    "is_error": True,
                                    "content": (
                                        "Your last response did not match the "
                                        f"required schema: {e}. Call the tool "
                                        "again with corrected arguments."
                                    ),
                                }
                            ],
                        }
                    )
                    continue

        raise LLMResponseError(
            f"LLM output did not match {output_model.__name__} after retrying: {last_error}"
        ) from last_error

    def _call_with_retry(self, system_prompt: str, messages: list[dict], tool_schema: dict):
        """
        The actual API call, wrapped with automatic retry for transient
        errors (rate limits, timeouts, connection issues, 5xx). Errors that
        won't be fixed by retrying (bad API key, malformed request) are
        raised immediately instead of wasting time retrying.
        """

        @retry(
            retry=retry_if_exception_type(_RETRYABLE_ANTHROPIC_ERRORS),
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential_jitter(initial=1, max=20),
            reraise=True,
        )
        def _do_call():
            start = time.monotonic()
            try:
                response = self._client.messages.create(
                    model=self.model,
                    max_tokens=self.max_output_tokens,
                    system=system_prompt,
                    messages=messages,
                    tools=[tool_schema],
                    tool_choice={"type": "tool", "name": tool_schema["name"]},
                )
                elapsed = time.monotonic() - start
                logger.info(
                    "LLM call ok | model=%s | elapsed=%.2fs | input_tokens=%s | output_tokens=%s",
                    self.model,
                    elapsed,
                    response.usage.input_tokens,
                    response.usage.output_tokens,
                )
                return response
            except anthropic.AuthenticationError as e:
                # Never retryable — the key itself is the problem.
                raise LLMAuthenticationError(f"Anthropic API key rejected: {e}") from e
            except anthropic.RateLimitError as e:
                logger.warning("LLM rate limited, will retry: %s", e)
                raise
            except anthropic.APITimeoutError as e:
                logger.warning("LLM call timed out, will retry: %s", e)
                raise
            except anthropic.APIConnectionError as e:
                logger.warning("LLM connection error, will retry: %s", e)
                raise
            except anthropic.BadRequestError as e:
                # A malformed request (e.g. bad schema) — retrying identical
                # input won't help, so fail fast with a clear message.
                raise LLMResponseError(f"Anthropic rejected the request: {e}") from e

        try:
            return _do_call()
        except anthropic.RateLimitError as e:
            raise LLMRateLimitError(
                f"Anthropic rate limit exceeded after {self.max_retries} attempts: {e}"
            ) from e
        except anthropic.APITimeoutError as e:
            raise LLMTimeoutError(
                f"Anthropic request timed out after {self.max_retries} attempts: {e}"
            ) from e
        except anthropic.APIConnectionError as e:
            raise LLMConnectionError(
                f"Could not reach Anthropic after {self.max_retries} attempts: {e}"
            ) from e
