"""
xAI Grok LLM Provider implementation.
Connects to xAI Grok API (OpenAI-compatible endpoint at https://api.x.ai/v1).
"""

import time
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI
from providers.base import LLMProvider, LLMResponse, TokenUsage


class GrokProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.x.ai/v1"):
        super().__init__(api_key)
        self.base_url = base_url
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url) if api_key else None

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str = "grok-2-latest",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format_json: bool = False,
        system_prompt: Optional[str] = None,
    ) -> LLMResponse:
        if not self.client:
            raise ValueError("Grok (xAI) API Key is missing. Set GROK_API_KEY or XAI_API_KEY environment variable.")

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Enable JSON mode if requested
        if response_format_json:
            kwargs["response_format"] = {"type": "json_object"}

        start_time = time.perf_counter()
        response = await self.client.chat.completions.create(**kwargs)
        latency_ms = (time.perf_counter() - start_time) * 1000

        content = response.choices[0].message.content or ""
        finish_reason = response.choices[0].finish_reason

        prompt_tokens = response.usage.prompt_tokens if response.usage else 0
        completion_tokens = response.usage.completion_tokens if response.usage else 0
        total_tokens = response.usage.total_tokens if response.usage else 0

        # Cost estimation: approx $2/1M input, $10/1M output for grok-2
        cost = (prompt_tokens * 0.000002) + (completion_tokens * 0.000010)

        parsed_json = self.extract_json(content) if response_format_json else None

        return LLMResponse(
            content=content,
            parsed_json=parsed_json,
            token_usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=cost,
            ),
            latency_ms=latency_ms,
            model=model,
            provider="grok",
            finish_reason=finish_reason,
        )
