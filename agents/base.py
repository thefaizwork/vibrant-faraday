"""
Base Agent Abstraction.
Provides lifecycle tracking, provider routing, retry logic, error isolation, and telemetry.
"""

from abc import ABC, abstractmethod
import json
import logging
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from providers.base import LLMProvider, LLMResponse, TokenUsage
from providers.factory import ProviderFactory

logger = logging.getLogger(__name__)


class AgentTelemetry(BaseModel):
    agent_name: str
    provider: str
    model: str
    latency_ms: float = 0.0
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    success: bool = True
    error: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)


class BaseAgent(ABC):
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt

    def _get_provider_and_model(self) -> tuple[LLMProvider, str]:
        return ProviderFactory.get_provider_for_agent(self.name)

    async def execute_llm(
        self,
        prompt: str,
        response_format_json: bool = True,
        max_retries: int = 2,
    ) -> tuple[Optional[Dict[str, Any]], str, AgentTelemetry]:
        """
        Executes the LLM with retry, json validation, and telemetry tracking.
        Returns: (parsed_json, raw_content, telemetry)
        """
        provider, model = self._get_provider_and_model()
        messages = [{"role": "user", "content": prompt}]
        
        telemetry = AgentTelemetry(
            agent_name=self.name,
            provider=getattr(provider, "__class__", type(provider)).__name__,
            model=model,
        )

        start_time = time.perf_counter()
        parsed_json = None
        raw_content = ""
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                response: LLMResponse = await provider.generate(
                    messages=messages,
                    model=model,
                    response_format_json=response_format_json,
                    system_prompt=self.system_prompt,
                )
                raw_content = response.content
                telemetry.token_usage = response.token_usage
                telemetry.latency_ms = response.latency_ms

                if response_format_json:
                    parsed_json = response.parsed_json or provider.extract_json(raw_content)
                    if not parsed_json:
                        raise ValueError(f"Agent {self.name} failed to return valid JSON output.")
                
                telemetry.success = True
                return parsed_json, raw_content, telemetry

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Agent {self.name} attempt {attempt} failed: {e}")
                if attempt == max_retries:
                    telemetry.success = False
                    telemetry.error = last_error
                    telemetry.latency_ms = (time.perf_counter() - start_time) * 1000
                    return None, raw_content, telemetry

        return None, raw_content, telemetry
