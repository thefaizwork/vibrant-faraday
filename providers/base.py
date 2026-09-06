"""
Base Provider abstraction for LLMs.
Ensures zero tight coupling between agents and specific LLM vendor SDKs.
"""

from abc import ABC, abstractmethod
import json
import re
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0


class LLMResponse(BaseModel):
    content: str
    parsed_json: Optional[Dict[str, Any]] = None
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    latency_ms: float = 0.0
    model: str = ""
    provider: str = ""
    finish_reason: Optional[str] = "stop"


class LLMProvider(ABC):
    """Abstract base class for all LLM providers (OpenAI, Anthropic, Mock)."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format_json: bool = False,
        system_prompt: Optional[str] = None,
    ) -> LLMResponse:
        """Generate text completion from LLM."""
        pass

    @staticmethod
    def extract_json(text: str) -> Optional[Dict[str, Any]]:
        """
        Robustly extracts and repairs JSON from LLM output, stripping markdown code fences,
        handling unescaped control characters, and falling back to regex field extraction.
        """
        if not text:
            return None

        clean_text = text.strip()

        # 1. Check for ```json ... ``` code fence
        json_fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean_text, re.IGNORECASE)
        if json_fence_match:
            clean_text = json_fence_match.group(1).strip()

        # 2. Try direct json parse with non-strict parsing
        try:
            return json.loads(clean_text, strict=False)
        except Exception:
            pass

        # 3. Try to find outermost { ... }
        start_brace = clean_text.find("{")
        end_brace = clean_text.rfind("}")
        if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
            candidate = clean_text[start_brace : end_brace + 1]
            try:
                return json.loads(candidate, strict=False)
            except Exception:
                # Attempt light sanitization (strip single-line & multi-line comments and trailing commas)
                sanitized = re.sub(r"/\*[\s\S]*?\*/", "", candidate)
                sanitized = re.sub(r"//.*$", "", sanitized, flags=re.MULTILINE)
                sanitized = re.sub(r",\s*([\}\]])", r"\1", sanitized)
                try:
                    return json.loads(sanitized, strict=False)
                except Exception:
                    pass

        # 4. Regex extraction fallback for HTML, CSS, JavaScript fields
        html_match = re.search(r'"html"\s*:\s*"([\s\S]*?)"\s*,\s*"css"', clean_text)
        css_match = re.search(r'"css"\s*:\s*"([\s\S]*?)"\s*,\s*"javascript"', clean_text)
        js_match = re.search(r'"javascript"\s*:\s*"([\s\S]*?)"\s*(?:,\s*"|\})', clean_text)

        if html_match and css_match:
            def _clean_str(s: str) -> str:
                return s.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')

            return {
                "html": _clean_str(html_match.group(1)),
                "css": _clean_str(css_match.group(1)),
                "javascript": _clean_str(js_match.group(1)) if js_match else "",
                "metadata": {"title": "Synthesized Candidate", "responsive": True},
                "component_structure": [],
                "design_rationale": "Extracted from candidate generator response."
            }

        return None
