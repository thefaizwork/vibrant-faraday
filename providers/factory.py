"""
Provider Factory & Dispatcher.
Instantiates, caches, and routes LLM providers per agent configuration.
"""

from typing import Dict, Optional
from config.settings import AgentModelConfig, ProviderType, settings
from providers.anthropic_provider import AnthropicProvider
from providers.base import LLMProvider
from providers.grok_provider import GrokProvider
from providers.groq_provider import GroqProvider
from providers.mock_provider import MockProvider
from providers.openai_provider import OpenAIProvider


class ProviderFactory:
    _instances: Dict[str, LLMProvider] = {}

    @classmethod
    def get_provider(cls, provider_type: ProviderType, api_key: Optional[str] = None) -> LLMProvider:
        """Get or create cached provider instance."""
        cache_key = f"{provider_type.value}_{api_key or 'default'}"
        if cache_key in cls._instances:
            return cls._instances[cache_key]

        provider: LLMProvider
        if provider_type == ProviderType.OPENAI:
            key = api_key or settings.openai_api_key
            provider = OpenAIProvider(api_key=key) if key else MockProvider()

        elif provider_type == ProviderType.ANTHROPIC:
            key = api_key or settings.anthropic_api_key
            provider = AnthropicProvider(api_key=key) if key else MockProvider()

        elif provider_type == ProviderType.GROK:
            key = api_key or settings.grok_api_key or settings.xai_api_key
            provider = GrokProvider(api_key=key) if key else MockProvider()

        elif provider_type == ProviderType.GROQ:
            key = api_key or settings.groq_api_key
            provider = GroqProvider(api_key=key) if key else MockProvider()

        else:
            provider = MockProvider()

        cls._instances[cache_key] = provider
        return provider

    @classmethod
    def get_provider_for_agent(cls, agent_name: str) -> tuple[LLMProvider, str]:
        """
        Returns (LLMProvider, model_name) configured for a given agent.
        """
        config: AgentModelConfig = settings.get_agent_config(agent_name)
        provider = cls.get_provider(config.provider)
        return provider, config.model
