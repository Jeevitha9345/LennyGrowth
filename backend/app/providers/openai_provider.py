import time
import logging
import httpx
from typing import List, Dict, Any

from app.config import settings
from app.providers.base import BaseModelProvider, ProviderResponse, ProviderHealth

logger = logging.getLogger("lenny_growth.providers.openai")

class OpenAIProvider(BaseModelProvider):
    def __init__(self):
        self.api_key = settings.openai_api_key.strip()
        self.model = settings.openai_model
        self.timeout = settings.openai_timeout_seconds
        self.endpoint = "https://api.openai.com/v1/chat/completions"

    async def health_check(self) -> ProviderHealth:
        if not self.api_key:
            return ProviderHealth(
                provider_name="openai",
                healthy=False,
                detail="OPENAI_API_KEY is not configured in environment."
            )
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get("https://api.openai.com/v1/models", headers=headers)
                if res.status_code == 200:
                    return ProviderHealth(
                        provider_name="openai",
                        healthy=True,
                        detail=f"OpenAI authenticated successfully with model '{self.model}'."
                    )
                return ProviderHealth(
                    provider_name="openai",
                    healthy=False,
                    detail=f"OpenAI authentication failed with status {res.status_code}"
                )
        except Exception as e:
            return ProviderHealth(
                provider_name="openai",
                healthy=False,
                detail=f"OpenAI connection error: {str(e)}"
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
                provider_name="openai",
                model_name=self.model,
                latency_ms=0.0,
                error="OPENAI_API_KEY is missing. Please set it in .env or switch to another provider."
            )

        start_time = time.perf_counter()
        openai_messages = [{"role": "system", "content": system_prompt}]
        openai_messages.extend(messages)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": openai_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(self.endpoint, headers=headers, json=payload)
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0

                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {})
                    return ProviderResponse(
                        content=content,
                        provider_name="openai",
                        model_name=self.model,
                        latency_ms=round(elapsed_ms, 2),
                        usage=usage
                    )
                else:
                    return ProviderResponse(
                        content="",
                        provider_name="openai",
                        model_name=self.model,
                        latency_ms=round(elapsed_ms, 2),
                        error=f"OpenAI error {res.status_code}: {res.text}"
                    )
        except httpx.TimeoutException:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return ProviderResponse(
                content="",
                provider_name="openai",
                model_name=self.model,
                latency_ms=round(elapsed_ms, 2),
                error=f"OpenAI request timed out after {self.timeout}s."
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return ProviderResponse(
                content="",
                provider_name="openai",
                model_name=self.model,
                latency_ms=round(elapsed_ms, 2),
                error=f"OpenAI communication failure: {str(e)}"
            )
