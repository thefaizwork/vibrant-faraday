"""
Anthropic LLM Provider implementation.
"""

import time
from typing import Any, Dict, List, Optional
from anthropic import AsyncAnthropic
from providers.base import LLMProvider, LLMResponse, TokenUsage


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.client = AsyncAnthropic(api_key=api_key) if api_key else None

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format_json: bool = False,
        system_prompt: Optional[str] = None,
    ) -> LLMResponse:
        if not self.client:
            raise ValueError("Anthropic API Key is missing. Set ANTHROPIC_API_KEY environment variable.")

        # Extract system message if present in messages
        sys_msg = system_prompt or ""
        anthropic_messages = []
        for m in messages:
            if m.get("role") == "system":
                sys_msg = (sys_msg + "\n" + m.get("content", "")).strip()
            else:
                anthropic_messages.append({"role": m.get("role", "user"), "content": m.get("content", "")})

        if response_format_json and sys_msg:
            sys_msg += "\nYou MUST return only a valid, strictly formatted JSON object without markdown fences or additional conversational prose."

        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": anthropic_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if sys_msg:
            kwargs["system"] = sys_msg

        start_time = time.perf_counter()
        response = await self.client.messages.create(**kwargs)
        latency_ms = (time.perf_counter() - start_time) * 1000

        content = ""
        for block in response.content:
            if hasattr(block, "text"):
                content += block.text

        finish_reason = response.stop_reason

        prompt_tokens = response.usage.input_tokens if response.usage else 0
        completion_tokens = response.usage.output_tokens if response.usage else 0
        total_tokens = prompt_tokens + completion_tokens

        # Cost estimation: Claude 3.5 Sonnet (~$3/1M in, $15/1M out)
        cost = (prompt_tokens * 0.000003) + (completion_tokens * 0.000015)

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
            provider="anthropic",
            finish_reason=finish_reason,
        )
