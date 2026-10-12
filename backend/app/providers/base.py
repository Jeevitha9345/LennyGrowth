from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ProviderResponse(BaseModel):
    content: str
    provider_name: str
    model_name: str
    latency_ms: float
    usage: Optional[Dict[str, int]] = None
    error: Optional[str] = None

class ProviderHealth(BaseModel):
    provider_name: str
    healthy: bool
    detail: str

class BaseModelProvider(ABC):
    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1024
    ) -> ProviderResponse:
        pass

    @abstractmethod
    async def health_check(self) -> ProviderHealth:
        pass
