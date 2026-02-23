import requests
import json
from typing import Optional

class AIClient:
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url

    def generate(self, prompt: str, model: str = "openrouter/anthropic/claude-3-haiku", max_tokens: int = 500) -> str:
        """
        Call the OpenClaw AI server (OpenRouter) to generate text.
        """
        try:
            resp = requests.post(
                f"{self.base_url}/v1/completions",
                json={
                    "model": model,
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                },
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("choices", [{}])[0].get("text", "").strip()
        except Exception as e:
            print(f"AI request error: {e}")
            return ""

ai_client = AIClient()
