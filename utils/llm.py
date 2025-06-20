"""LLM client utilities."""

import os
import openai
from .network import get_proxy_client
from .config import CHAT_BASE_URL
from .keys import get_api_key


def get_chat_client() -> openai.OpenAI:
    """Return an OpenAI-compatible client for chat completions.

    Uses ``CHAT_BASE_URL`` from config to connect to a local LLM if set.
    For OpenAI's API, uses the regular ``OPENAI_API_KEY`` environment variable.
    """
    kwargs = {"http_client": get_proxy_client()}
    if CHAT_BASE_URL:
        kwargs["base_url"] = CHAT_BASE_URL
        # Local servers typically don't require an API key but the OpenAI
        # client expects one, so provide a placeholder if none is set.
        kwargs["api_key"] = os.getenv("OPENAI_API_KEY", "local-api-key")
    else:
        kwargs["api_key"] = get_api_key()
    return openai.OpenAI(**kwargs)


def get_openai_client() -> openai.OpenAI:
    """Return a client that always targets OpenAI's servers."""
    return openai.OpenAI(api_key=get_api_key(), http_client=get_proxy_client())
