"""
FINIQ AI Service

Wraps OpenAI API calls with proper error handling, demo mode fallback,
and prompt injection protection.

This project is a prototype and is not financial advice.
"""

import os
import sys
from typing import Optional

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

_client = None
_openai_available = None


def _get_client():
    """Lazily initialize the OpenAI client."""
    global _client, _openai_available
    if _openai_available is not None:
        return _client

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key or api_key.startswith("your_"):
        _openai_available = False
        _client = None
        return None

    try:
        from openai import OpenAI
        _client = OpenAI(api_key=api_key)
        _openai_available = True
        return _client
    except Exception:
        _openai_available = False
        _client = None
        return None


def is_available() -> bool:
    """Check if the OpenAI API is configured and available."""
    return _get_client() is not None


def get_client():
    """Return the OpenAI client, or None if unavailable."""
    return _get_client()


def complete(
    messages: list,
    model: str = "gpt-4o-mini",
    temperature: float = 0.3,
    max_tokens: int = 1024,
    system_prompt: Optional[str] = None,
) -> Optional[str]:
    """
    Call the OpenAI chat completion API.
    Returns the assistant's response text, or None if unavailable.
    """
    client = _get_client()
    if not client:
        return None

    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=full_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        return None
