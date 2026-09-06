"""
Configuration settings for the Multi-Agent Web Design Generation System.
Supports environment variables, YAML config files, and per-agent model routing.
"""

from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SystemMode(str, Enum):
    GENERATOR_ONLY = "generator_only"
    GENERAL_CRITIC = "general_critic"
    SPECIALIZED_MULTI_AGENT = "specialized_multi_agent"


class ProviderType(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROK = "grok"
    GROQ = "groq"
    MOCK = "mock"


class AgentModelConfig(BaseSettings):
    provider: ProviderType = ProviderType.MOCK
    model: str = "mock-agent-v1"
    temperature: float = 0.7
    max_tokens: int = 4096


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix=""
    )

    # Global System Mode
    system_mode: SystemMode = SystemMode.SPECIALIZED_MULTI_AGENT

    # API Keys
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    grok_api_key: Optional[str] = Field(default=None, alias="GROK_API_KEY")
    xai_api_key: Optional[str] = Field(default=None, alias="XAI_API_KEY")
    groq_api_key: Optional[str] = Field(default=None, alias="GROQ_API_KEY")

    # Global LLM Provider Defaults
    default_provider: ProviderType = ProviderType.MOCK
    default_model: str = "mock-agent-v1"

    # Per-Agent Provider and Model Mappings (can be overridden via env vars or config)
    prompt_structurer_provider: ProviderType = Field(default=ProviderType.MOCK, alias="PROMPT_STRUCTURER_PROVIDER")
    prompt_structurer_model: str = Field(default="gpt-4o-mini", alias="PROMPT_STRUCTURER_MODEL")

    generator_provider: ProviderType = Field(default=ProviderType.MOCK, alias="GENERATOR_PROVIDER")
    generator_model: str = Field(default="claude-3-5-sonnet-20241022", alias="GENERATOR_MODEL")

    aesthetic_agent_provider: ProviderType = Field(default=ProviderType.MOCK, alias="AESTHETIC_AGENT_PROVIDER")
    aesthetic_agent_model: str = Field(default="gpt-4o", alias="AESTHETIC_AGENT_MODEL")

    accessibility_agent_provider: ProviderType = Field(default=ProviderType.MOCK, alias="ACCESSIBILITY_AGENT_PROVIDER")
    accessibility_agent_model: str = Field(default="gpt-4o", alias="ACCESSIBILITY_AGENT_MODEL")

    usability_agent_provider: ProviderType = Field(default=ProviderType.MOCK, alias="USABILITY_AGENT_PROVIDER")
    usability_agent_model: str = Field(default="gpt-4o", alias="USABILITY_AGENT_MODEL")

    ethics_agent_provider: ProviderType = Field(default=ProviderType.MOCK, alias="ETHICS_AGENT_PROVIDER")
    ethics_agent_model: str = Field(default="gpt-4o", alias="ETHICS_AGENT_MODEL")

    originality_agent_provider: ProviderType = Field(default=ProviderType.MOCK, alias="ORIGINALITY_AGENT_PROVIDER")
    originality_agent_model: str = Field(default="gpt-4o", alias="ORIGINALITY_AGENT_MODEL")

    general_critic_provider: ProviderType = Field(default=ProviderType.MOCK, alias="GENERAL_CRITIC_PROVIDER")
    general_critic_model: str = Field(default="gpt-4o", alias="GENERAL_CRITIC_MODEL")

    aggregator_provider: ProviderType = Field(default=ProviderType.MOCK, alias="AGGREGATOR_PROVIDER")
    aggregator_model: str = Field(default="gpt-4o", alias="AGGREGATOR_MODEL")

    refiner_provider: ProviderType = Field(default=ProviderType.MOCK, alias="REFINER_PROVIDER")
    refiner_model: str = Field(default="claude-3-5-sonnet-20241022", alias="REFINER_MODEL")

    # Orchestration & Threshold Controls
    max_iterations: int = Field(default=3, alias="MAX_ITERATIONS")
    quality_threshold: float = Field(default=8.0, alias="QUALITY_THRESHOLD")
    cost_limit_usd: float = Field(default=2.00, alias="COST_LIMIT")
    time_limit_seconds: int = Field(default=120, alias="TIME_LIMIT")
    
    # Workspace & Database
    workspace_dir: Path = Field(default=Path("./runs"), alias="WORKSPACE_DIR")
    database_url: str = Field(default="sqlite:///./runs/research_system.db", alias="DATABASE_URL")
    
    # Server & API
    host: str = "0.0.0.0"
    port: int = 8000
    mcp_port: int = 8001
    cors_origins: List[str] = ["*"]

    def get_agent_config(self, agent_name: str) -> AgentModelConfig:
        """Returns the AgentModelConfig for a specific agent based on settings."""
        agent_name_norm = agent_name.lower().replace("-", "_").replace(" ", "_")
        
        provider_attr = f"{agent_name_norm}_provider"
        model_attr = f"{agent_name_norm}_model"
        
        provider = getattr(self, provider_attr, self.default_provider)
        model = getattr(self, model_attr, self.default_model)
        
        # If API key is missing for live providers, auto-fallback to Mock for safety
        if provider == ProviderType.OPENAI and not self.openai_api_key:
            provider = ProviderType.MOCK
        elif provider == ProviderType.ANTHROPIC and not self.anthropic_api_key:
            provider = ProviderType.MOCK
        elif provider == ProviderType.GROK and not (self.grok_api_key or self.xai_api_key):
            provider = ProviderType.MOCK
        elif provider == ProviderType.GROQ and not self.groq_api_key:
            provider = ProviderType.MOCK
            
        return AgentModelConfig(provider=provider, model=model)

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> "Settings":
        """Load settings with overrides from a YAML file."""
        if yaml_path.exists():
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            return cls(**data)
        return cls()


# Global settings instance
settings = Settings()
