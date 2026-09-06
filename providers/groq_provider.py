"""
Groq Cloud LLM Provider implementation.
Connects to Groq Cloud ultra-fast inference API (OpenAI-compatible at https://api.groq.com/openai/v1).
Includes automatic rate limit backoff and JSON mode recovery.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI, RateLimitError, BadRequestError
from providers.base import LLMProvider, LLMResponse, TokenUsage


class GroqProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.groq.com/openai/v1"):
        super().__init__(api_key)
        self.base_url = base_url
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url) if api_key else None

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str = "openai/gpt-oss-20b",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format_json: bool = False,
        system_prompt: Optional[str] = None,
    ) -> LLMResponse:
        if not self.client:
            raise ValueError("Groq API Key is missing. Set GROQ_API_KEY environment variable.")

        formatted_messages = []
        sys_content = system_prompt or ""
        if response_format_json:
            sys_content += "\nRespond strictly in valid JSON format."

        if sys_content:
            formatted_messages.append({"role": "system", "content": sys_content})
        
        for m in messages:
            content = m.get("content", "")
            if response_format_json and "json" not in content.lower():
                content += "\nReturn output as JSON."
            formatted_messages.append({"role": m.get("role", "user"), "content": content})

        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format_json:
            kwargs["response_format"] = {"type": "json_object"}


        start_time = time.perf_counter()
        
        # Retry loop for rate limits and fallback for json_validate_failed
        response = None
        for attempt in range(3):
            try:
                response = await self.client.chat.completions.create(**kwargs)
                break
            except RateLimitError:
                if attempt < 2:
                    await asyncio.sleep(3.0 * (attempt + 1))
                else:
                    raise
            except BadRequestError as e:
                # If JSON validate failed, retry without response_format constraint
                if "json_validate_failed" in str(e) or "response_format" in kwargs:
                    kwargs.pop("response_format", None)
                    response = await self.client.chat.completions.create(**kwargs)
                    break
                raise

        latency_ms = (time.perf_counter() - start_time) * 1000

        content = response.choices[0].message.content or ""
        finish_reason = response.choices[0].finish_reason

        prompt_tokens = response.usage.prompt_tokens if response.usage else 0
        completion_tokens = response.usage.completion_tokens if response.usage else 0
        total_tokens = response.usage.total_tokens if response.usage else 0

        # Cost estimation: approx $0.15/1M
        cost = (prompt_tokens * 0.00000015) + (completion_tokens * 0.00000020)

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
            provider="groq",
            finish_reason=finish_reason,
        )
