"""
Unit tests for Provider abstraction including Grok and Groq.
"""

import pytest
from providers.base import LLMProvider, TokenUsage, LLMResponse
from providers.factory import ProviderFactory
from providers.grok_provider import GrokProvider
from providers.groq_provider import GroqProvider
from providers.mock_provider import MockProvider
from config.settings import ProviderType


@pytest.mark.asyncio
async def test_mock_provider_generation():
    provider = MockProvider()
    response = await provider.generate(
        messages=[{"role": "user", "content": "Create prompt structurer for e-commerce website"}],
        model="mock-agent-v1",
        response_format_json=True
    )
    assert response.parsed_json is not None
    assert "project_goal" in response.parsed_json
    assert "website_type" in response.parsed_json
    assert response.token_usage.total_tokens > 0


def test_json_extraction():
    raw_with_fences = '```json\n{"score": 8.5, "issues": ["contrast"]}\n```'
    extracted = LLMProvider.extract_json(raw_with_fences)
    assert extracted is not None
    assert extracted["score"] == 8.5
    assert "contrast" in extracted["issues"]

    raw_conversational = 'Sure! Here is the output:\n{"status": "ok"}\nHope this helps!'
    extracted2 = LLMProvider.extract_json(raw_conversational)
    assert extracted2 is not None
    assert extracted2["status"] == "ok"


def test_provider_factory():
    provider = ProviderFactory.get_provider(ProviderType.MOCK)
    assert isinstance(provider, MockProvider)

    # Grok with key
    grok = ProviderFactory.get_provider(ProviderType.GROK, api_key="xai-test-key")
    assert isinstance(grok, GrokProvider)
    assert grok.base_url == "https://api.x.ai/v1"

    # Groq with key
    groq = ProviderFactory.get_provider(ProviderType.GROQ, api_key="gsk-test-key")
    assert isinstance(groq, GroqProvider)
    assert groq.base_url == "https://api.groq.com/openai/v1"
