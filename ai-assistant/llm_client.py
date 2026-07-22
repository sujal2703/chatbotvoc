"""
llm_client.py

Thin wrapper around the OpenAI API. Keeping this separate from app.py means
the routes don't need to know anything about the underlying LLM provider —
if you ever swap providers, only this file changes.
"""

import os
from openai import OpenAI, APIError, AuthenticationError

MODEL_NAME = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


class LLMConfigError(Exception):
    """Raised when the API key is missing or invalid."""
    pass


class LLMRequestError(Exception):
    """Raised when the API call itself fails (network, rate limit, etc.)."""
    pass


def _get_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise LLMConfigError(
            "No OPENAI_API_KEY found in environment. "
            "Set it before running the app (see .env.example)."
        )
    base_url = os.environ.get("OPENAI_BASE_URL")
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def generate_response(prompt_text: str) -> str:
    """
    Sends a fully-formatted prompt string to the LLM and returns the
    plain-text response. Raises LLMConfigError or LLMRequestError on failure
    so the calling route can show a friendly message instead of crashing.
    """
    client = _get_client()
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt_text},
            ],
            max_tokens=500,
            temperature=0.8,
        )
        return completion.choices[0].message.content.strip()
    except AuthenticationError:
        raise LLMConfigError(
            "The OPENAI_API_KEY provided was rejected by the API. "
            "Double-check that it's valid."
        )
    except APIError as e:
        raise LLMRequestError(f"The LLM API returned an error: {e}")
    except Exception as e:
        raise LLMRequestError(f"Unexpected error while calling the LLM API: {e}")
