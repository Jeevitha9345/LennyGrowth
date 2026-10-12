import logging
from typing import Dict

from app.config import settings
from app.providers.base import BaseModelProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.mock_provider import MockProvider

logger = logging.getLogger("lenny_growth.providers.factory")

class ProviderFactory:
    def __init__(self):
        self._instances: Dict[str, BaseModelProvider] = {
            "mock": MockProvider(),
            "ollama": OllamaProvider(),
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
        }

    def get_provider(self, provider_name: str = None) -> BaseModelProvider:
        target = (provider_name or settings.active_provider).lower().strip()
        if target in self._instances:
            return self._instances[target]
        logger.warning(f"Unknown provider '{target}' requested. Falling back to mock provider.")
        return self._instances["mock"]

    def get_active_provider_name(self, override: str = None) -> str:
        target = (override or settings.active_provider).lower().strip()
        if target in self._instances:
            return target
        return "mock"

provider_factory = ProviderFactory()
