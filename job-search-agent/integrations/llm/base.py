"""
integrations/llm/base.py
-------------------------
Defines the CONTRACT every LLM provider must follow, and the errors any
provider can raise. No other file in this project imports `anthropic`
directly except `anthropic_provider.py` — everyone else (agents) imports
from here instead.

WHY THIS FILE EXISTS:
If `agents/job_matcher.py` called `anthropic.Anthropic()` directly, we'd
be locked into Anthropic forever, and every agent would duplicate its own
retry/error-handling logic. Instead:

  - `LLMProvider` is an abstract base class: "any provider must implement
    a `complete_structured` method with this exact signature."
  - `anthropic_provider.py` is ONE implementation of that contract.
  - Tomorrow, an `openai_provider.py` could implement the same contract,
    and agents wouldn't need to change a single line.

This is the same idea as a USB port: agents plug into `LLMProvider`, not
into "Anthropic" or "OpenAI" specifically.
"""

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMError(Exception):
    """Base class for every error this layer can raise."""


class LLMAuthenticationError(LLMError):
    """The API key is missing, invalid, or revoked. Not retryable — fix
    your .env, then try again."""


class LLMRateLimitError(LLMError):
    """You've hit the provider's rate limit. Retryable after a delay."""


class LLMTimeoutError(LLMError):
    """The request took too long. Retryable."""


class LLMConnectionError(LLMError):
    """A network-level problem reaching the provider. Retryable."""


class LLMResponseError(LLMError):
    """The provider responded, but its output didn't match the schema we
    asked for (even after a retry). Not retryable — usually means the
    prompt needs adjusting, not that you should call again immediately."""


class LLMProvider(ABC):
    """
    Abstract interface every LLM provider must implement.

    `complete_structured` is the ONLY method agents call. It takes a
    system prompt (the ground rules), a user prompt (the actual task +
    data), and a Pydantic model class describing the exact shape of the
    answer you want back. It returns a validated instance of that model —
    never raw text, never a dict you have to trust.
    """

    @abstractmethod
    def complete_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        output_model: type[T],
    ) -> T:
        """
        Ask the LLM to perform a task and return output matching
        `output_model`'s schema exactly.

        Raises:
            LLMAuthenticationError, LLMRateLimitError, LLMTimeoutError,
            LLMConnectionError, LLMResponseError
        """
        raise NotImplementedError
