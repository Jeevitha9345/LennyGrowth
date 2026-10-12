import time
import logging
import httpx
from typing import List, Dict, Any

from app.config import settings
from app.providers.base import BaseModelProvider, ProviderResponse, ProviderHealth

logger = logging.getLogger("lenny_growth.providers.ollama")

class OllamaProvider(BaseModelProvider):
    def __init__(self):
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model
        self.timeout = settings.ollama_timeout_seconds

    async def health_check(self) -> ProviderHealth:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    if any(self.model in m for m in models):
                        return ProviderHealth(
                            provider_name="ollama",
                            healthy=True,
                            detail=f"Ollama running with model '{self.model}' available."
                        )
                    else:
                        return ProviderHealth(
                            provider_name="ollama",
                            healthy=False,
                            detail=f"Ollama running at {self.base_url}, but model '{self.model}' is not pulled. Available: {models}"
                        )
                return ProviderHealth(
                    provider_name="ollama",
                    healthy=False,
                    detail=f"Ollama returned HTTP status {res.status_code}"
                )
        except Exception as e:
            return ProviderHealth(
                provider_name="ollama",
                healthy=False,
                detail=f"Ollama connection unreachable at {self.base_url}: {str(e)}"
            )

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1024
    ) -> ProviderResponse:
        start_time = time.perf_counter()
        
        # Build prompt payload for Ollama
        ollama_messages = [{"role": "system", "content": system_prompt}]
        ollama_messages.extend(messages)

        payload = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(f"{self.base_url}/api/chat", json=payload)
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0

                if res.status_code == 200:
                    data = res.json()
                    content = data.get("message", {}).get("content", "")
                    return ProviderResponse(
                        content=content,
                        provider_name="ollama",
                        model_name=self.model,
                        latency_ms=round(elapsed_ms, 2)
                    )
                else:
                    return ProviderResponse(
                        content="",
                        provider_name="ollama",
                        model_name=self.model,
                        latency_ms=round(elapsed_ms, 2),
                        error=f"Ollama error {res.status_code}: {res.text}"
                    )
        except httpx.TimeoutException:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return ProviderResponse(
                content="",
                provider_name="ollama",
                model_name=self.model,
                latency_ms=round(elapsed_ms, 2),
                error=f"Ollama request timed out after {self.timeout}s. For strict ~1GB RAM CPU environment, consider switching to Cloud or Mock provider."
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return ProviderResponse(
                content="",
                provider_name="ollama",
                model_name=self.model,
                latency_ms=round(elapsed_ms, 2),
                error=f"Failed to communicate with Ollama: {str(e)}"
            )
