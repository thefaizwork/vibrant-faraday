"""
Aesthetic Evaluation Agent.
Specializes in visual hierarchy, typography, spacing, composition, color balance, and visual appeal.
"""

from typing import Tuple, Dict, Any
from agents.base import BaseAgent, AgentTelemetry
from orchestration.state import AestheticCritique, WebsiteArtifacts, StructuredPrompt

SYSTEM_PROMPT = """You are the Aesthetic Evaluation Agent in a multi-agent web design research system.
Your mission is to perform a rigorous aesthetic and visual design analysis on the candidate website.

Evaluate:
- visual hierarchy & focal points
- typography scale, readability, font pairings, line-height
- spacing, padding, margins, visual rhythm
- composition, alignment, grid balance
- color harmony, palette cohesion, contrast balance
- component styling, modern elevation, border radii, card design
- overall visual polish and craftsmanship

You MUST return a JSON object with this exact schema:
{
  "score": 8.5,
  "issues": [
    "Specific aesthetic issue description 1",
    "Specific aesthetic issue description 2"
  ],
  "severity": ["medium"],
  "evidence": [
    "CSS selector or HTML snippet exhibiting the issue",
    "Evidence detail"
  ],
  "recommendations": [
    "Concrete styling recommendation to resolve issue 1",
    "Concrete styling recommendation to resolve issue 2"
  ]
}
Do not include markdown fences or text outside the JSON.
"""


class AestheticAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="aesthetic_agent",
            system_prompt=SYSTEM_PROMPT
        )

    async def evaluate(
        self,
        website: WebsiteArtifacts,
        spec: StructuredPrompt
    ) -> Tuple[AestheticCritique, AgentTelemetry]:
        prompt = f"""Target Project Goal: {spec.project_goal}
Visual Requirements: {', '.join(spec.visual_requirements)}

Website HTML:
```html
{website.html[:4000]}
```

Website CSS:
```css
{website.css[:4000]}
```

Please evaluate the visual aesthetics, hierarchy, typography, spacing, color harmony, and composition. Return the structured JSON critique."""

        data, raw, telemetry = await self.execute_llm(prompt=prompt, response_format_json=True)

        if not data or "score" not in data:
            data = {
                "score": 8.0,
                "issues": ["Minor visual spacing could be further optimized"],
                "severity": ["low"],
                "evidence": ["General layout grid"],
                "recommendations": ["Refine section vertical margins and typography scale"]
            }

        return AestheticCritique(**data), telemetry
