"""
integrations/llm/__init__.py
-----------------------------
A tiny factory so the rest of the app never has to know which concrete
provider class to import. Today it always returns the Anthropic provider;
if you add another provider later (e.g. OpenAI), this is the one place
that changes — agents keep calling `get_llm_provider()` unchanged.
"""

from integrations.llm.anthropic_provider import AnthropicLLMProvider
from integrations.llm.base import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMError,
    LLMProvider,
    LLMRateLimitError,
    LLMResponseError,
    LLMTimeoutError,
)

__all__ = [
    "get_llm_provider",
    "LLMProvider",
    "LLMError",
    "LLMAuthenticationError",
    "LLMRateLimitError",
    "LLMTimeoutError",
    "LLMConnectionError",
    "LLMResponseError",
]


def get_llm_provider() -> LLMProvider:
    """Return the LLM provider the whole app should use."""
    return AnthropicLLMProvider()
