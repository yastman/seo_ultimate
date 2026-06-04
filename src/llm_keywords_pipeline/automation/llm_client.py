"""Provider-agnostic LLM client (issue #19).

LlmClient interface + HTTP implementation (env-configured).
Keys are read from environment; never logged.
"""
from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from string import Template
from typing import Any


@dataclass
class LlmUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0


@dataclass
class LlmResponse:
    text: str
    usage: LlmUsage = field(default_factory=LlmUsage)
    model: str = ""
    latency_ms: int = 0


class LlmClient(ABC):
    """Abstract provider-agnostic LLM interface."""

    @abstractmethod
    def complete(self, prompt: str, **kwargs: Any) -> LlmResponse:
        """Send a prompt and return the completion."""

    def produce(self, brief: str) -> LlmResponse:
        """Generate content draft from a brief."""
        return self.complete(brief)

    def revise(self, draft: str, failures: list[dict]) -> LlmResponse:
        """Revise a draft given a list of failed check payloads."""
        failures_text = "\n".join(
            f"- [{f['id']}] {f['message']} (expected: {f['expected']}, got: {f['actual']})"
            for f in failures
        )
        prompt = (
            f"Revise the following content to fix these validation failures:\n\n"
            f"{failures_text}\n\n"
            f"--- CONTENT ---\n{draft}"
        )
        return self.complete(prompt)


class MockLlmClient(LlmClient):
    """Deterministic mock for testing — echoes prompt back as a minimal draft."""

    def __init__(self, fixed_response: str = "# Заголовок\n\nТестовый контент категории."):
        self._response = fixed_response
        self.calls: list[str] = []

    def complete(self, prompt: str, **kwargs: Any) -> LlmResponse:
        self.calls.append(prompt)
        return LlmResponse(
            text=self._response,
            usage=LlmUsage(prompt_tokens=len(prompt.split()), completion_tokens=10, cost_usd=0.0),
            model="mock",
            latency_ms=0,
        )


class HttpLlmClient(LlmClient):
    """HTTP-based provider (OpenAI-compatible API). Keys from env."""

    def __init__(
        self,
        endpoint: str | None = None,
        model: str | None = None,
        api_key_env: str = "LLM_API_KEY",
        timeout: int = 60,
        max_retries: int = 3,
    ):
        import requests  # noqa: PLC0415 (lazy — optional at import time)
        self._requests = requests
        self.endpoint = endpoint or os.getenv("LLM_ENDPOINT", "https://api.openai.com/v1/chat/completions")
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")
        self._api_key_env = api_key_env
        self.timeout = timeout
        self.max_retries = max_retries

    def _api_key(self) -> str:
        key = os.getenv(self._api_key_env, "")
        if not key:
            raise ValueError(f"LLM API key missing. Set {self._api_key_env} env var.")
        return key

    def complete(self, prompt: str, **kwargs: Any) -> LlmResponse:
        headers = {
            "Authorization": f"Bearer {self._api_key()}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            **kwargs,
        }
        last_exc: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                t0 = time.monotonic()
                resp = self._requests.post(self.endpoint, json=payload, headers=headers, timeout=self.timeout)
                latency = int((time.monotonic() - t0) * 1000)
                resp.raise_for_status()
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                usage_data = data.get("usage", {})
                return LlmResponse(
                    text=text,
                    usage=LlmUsage(
                        prompt_tokens=usage_data.get("prompt_tokens", 0),
                        completion_tokens=usage_data.get("completion_tokens", 0),
                    ),
                    model=self.model,
                    latency_ms=latency,
                )
            except Exception as exc:
                last_exc = exc
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
        raise RuntimeError(f"LLM request failed after {self.max_retries} attempts") from last_exc


def render_prompt_template(template_path: Path, variables: dict) -> str:
    """Substitute {placeholders} in a prompt template file."""
    raw = template_path.read_text(encoding="utf-8")
    return Template(raw).safe_substitute(variables)
