import pytest
from app.providers.factory import provider_factory
from app.providers.mock_provider import MockProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.anthropic_provider import AnthropicProvider

@pytest.mark.asyncio
async def test_provider_factory_routing():
    mock_p = provider_factory.get_provider("mock")
    assert isinstance(mock_p, MockProvider)
    
    ollama_p = provider_factory.get_provider("ollama")
    assert isinstance(ollama_p, OllamaProvider)

    openai_p = provider_factory.get_provider("openai")
    assert isinstance(openai_p, OpenAIProvider)

    anthropic_p = provider_factory.get_provider("anthropic")
    assert isinstance(anthropic_p, AnthropicProvider)

    # Unknown provider falls back to mock
    fallback = provider_factory.get_provider("nonexistent")
    assert isinstance(fallback, MockProvider)

@pytest.mark.asyncio
async def test_mock_provider_generation():
    provider = MockProvider()
    health = await provider.health_check()
    assert health.healthy

    res = await provider.generate_response(
        messages=[{"role": "user", "content": "What is the LNO framework from Shreyas Doshi?"}],
        system_prompt="Grounded prompt"
    )
    assert res.content != ""
    assert "LNO" in res.content
    assert res.provider_name == "mock"
    assert res.latency_ms >= 0

@pytest.mark.asyncio
async def test_ollama_graceful_offline_handling():
    # Test when Ollama is offline or unconfigured
    provider = OllamaProvider()
    provider.base_url = "http://127.0.0.1:99999" # invalid port
    health = await provider.health_check()
    assert not health.healthy
    assert "unreachable" in health.detail.lower() or "failed" in health.detail.lower()
