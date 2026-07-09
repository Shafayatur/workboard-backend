"""
Thin wrapper around Gemini's REST API, shared by:
- tasks.views.ParseTaskView   (natural-language task entry)
- annotations.views.SuggestLabelView  (auto-label a drawn shape)

Kept deliberately simple: one function to call the model, one helper to
pull JSON out of a response that might be wrapped in markdown fences.
"""
import json
import re

import requests
from django.conf import settings

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_MODEL = "gemini-2.5-flash"


class GeminiError(Exception):
    """Raised for any failure talking to Gemini or parsing its response."""


def _extract_text(response_json):
    try:
        return response_json["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise GeminiError(f"Unexpected Gemini response shape: {response_json}") from exc


def call_gemini(parts, model=DEFAULT_MODEL, timeout=20):
    """
    parts: list of content parts, e.g.
        [{"text": "..."}]
        [{"text": "..."}, {"inline_data": {"mime_type": "image/png", "data": "<base64>"}}]
    Returns the model's raw text response.
    """
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    if not api_key:
        raise GeminiError("GEMINI_API_KEY is not configured on the server.")

    url = GEMINI_API_URL.format(model=model)
    payload = {"contents": [{"parts": parts}]}

    try:
        resp = requests.post(url, params={"key": api_key}, json=payload, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise GeminiError(f"Gemini request failed: {exc}") from exc

    return _extract_text(resp.json())


def extract_json(text):
    """Strip ```json ... ``` markdown fences if present, then parse as JSON."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)