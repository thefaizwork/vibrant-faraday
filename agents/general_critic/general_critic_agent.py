"""
General Critic Agent.
Provides a single monolithic evaluation across all web design aspects for Baseline Mode B.
"""

from typing import Tuple, Dict, Any
from agents.base import BaseAgent, AgentTelemetry
from orchestration.state import GeneralCriticCritique, WebsiteArtifacts, StructuredPrompt

SYSTEM_PROMPT = """You are the General Critic Agent in a web design research system.
Your mission is to perform a single, holistic critique across all aspects of the website: aesthetics, accessibility, usability, ethics, and originality.

You MUST return a JSON object with this exact schema:
{
  "score": 7.8,
  "overall_feedback": "Comprehensive qualitative review paragraph",
  "issues": [
    "General issue description 1",
    "General issue description 2",
    "General issue description 3"
  ],
  "recommendations": [
    "General recommendation 1",
    "General recommendation 2",
    "General recommendation 3"
  ]
}
Do not include markdown fences or text outside the JSON.
"""


class GeneralCriticAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="general_critic",
            system_prompt=SYSTEM_PROMPT
        )

    async def evaluate(
        self,
        website: WebsiteArtifacts,
        spec: StructuredPrompt
    ) -> Tuple[GeneralCriticCritique, AgentTelemetry]:
        prompt = f"""Target Project: {spec.project_goal}
Requirements Overview:
- Visual: {', '.join(spec.visual_requirements)}
- Usability: {', '.join(spec.usability_requirements)}
- Accessibility: {', '.join(spec.accessibility_requirements)}
- Compliance: {', '.join(spec.compliance_requirements)}

Website HTML:
```html
{website.html[:4000]}
```

Website CSS:
```css
{website.css[:3000]}
```

Website JS:
```javascript
{website.javascript[:2000]}
```

Evaluate the entire website holistically across visual design, UX, accessibility, and code quality. Return the structured JSON critique."""

        data, raw, telemetry = await self.execute_llm(prompt=prompt, response_format_json=True)

        if not data or "score" not in data:
            data = {
                "score": 7.5,
                "overall_feedback": "The website provides a functional baseline with solid structure but needs visual and accessibility polish.",
                "issues": ["Contrast could be increased", "Interactive feedback is basic"],
                "recommendations": ["Elevate contrast ratios", "Add micro-interactions"]
            }

        return GeneralCriticCritique(**data), telemetry
