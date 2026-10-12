import time
import logging
import httpx
from typing import List, Dict, Any

from app.config import settings
from app.providers.base import BaseModelProvider, ProviderResponse, ProviderHealth

logger = logging.getLogger("lenny_growth.providers.anthropic")

class AnthropicProvider(BaseModelProvider):
    def __init__(self):
        self.api_key = settings.anthropic_api_key.strip()
        self.model = settings.anthropic_model
        self.timeout = settings.anthropic_timeout_seconds
        self.endpoint = "https://api.anthropic.com/v1/messages"

    async def health_check(self) -> ProviderHealth:
        if not self.api_key:
            return ProviderHealth(
                provider_name="anthropic",
                healthy=False,
                detail="ANTHROPIC_API_KEY is not configured in environment."
            )
        return ProviderHealth(
            provider_name="anthropic",
            healthy=True,
            detail=f"Anthropic API key configured for model '{self.model}'."
        )

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1024
    ) -> ProviderResponse:
        if not self.api_key:
            return ProviderResponse(
                content="",
                provider_name="anthropic",
                model_name=self.model,
                latency_ms=0.0,
                error="ANTHROPIC_API_KEY is missing. Please set it in .env or switch to another provider."
            )

        start_time = time.perf_counter()
        
        # Format messages for Anthropic (user & assistant only in messages array, system in top-level param)
        anthropic_messages = []
        for m in messages:
            role = m.get("role", "user")
            if role in ["user", "assistant"]:
                anthropic_messages.append({
                    "role": role,
                    "content": m.get("content", "")
                })

        if not anthropic_messages:
            anthropic_messages.append({"role": "user", "content": "Hello"})

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "system": system_prompt,
            "messages": anthropic_messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(self.endpoint, headers=headers, json=payload)
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0

                if res.status_code == 200:
                    data = res.json()
                    content_blocks = data.get("content", [])
                    content = "".join([b.get("text", "") for b in content_blocks if b.get("type") == "text"])
                    usage = data.get("usage", {})
                    return ProviderResponse(
                        content=content,
                        provider_name="anthropic",
                        model_name=self.model,
                        latency_ms=round(elapsed_ms, 2),
                        usage=usage
                    )
                else:
                    return ProviderResponse(
                        content="",
                        provider_name="anthropic",
                        model_name=self.model,
                        latency_ms=round(elapsed_ms, 2),
                        error=f"Anthropic error {res.status_code}: {res.text}"
                    )
        except httpx.TimeoutException:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return ProviderResponse(
                content="",
                provider_name="anthropic",
                model_name=self.model,
                latency_ms=round(elapsed_ms, 2),
                error=f"Anthropic request timed out after {self.timeout}s."
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return ProviderResponse(
                content="",
                provider_name="anthropic",
                model_name=self.model,
                latency_ms=round(elapsed_ms, 2),
                error=f"Anthropic communication failure: {str(e)}"
            )
