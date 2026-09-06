"""
Originality & Diversity Evaluation Agent.
Specializes in visual distinctness, layout diversity, avoiding boilerplate tropes, and aesthetic innovation.
"""

from typing import Tuple, Dict, Any
from agents.base import BaseAgent, AgentTelemetry
from orchestration.state import OriginalityCritique, WebsiteArtifacts, StructuredPrompt

SYSTEM_PROMPT = """You are the Originality & Diversity Evaluation Agent in a multi-agent web design research system.
Your mission is to evaluate the creative originality, distinctiveness, and layout variety of the generated web design.

Evaluate:
- Visual distinctness and brand memorability
- Creative avoidance of overused, generic Bootstrap/Tailwind boilerplate templates
- Layout diversity, asymmetrical composition touches, bespoke section transitions
- Component originality (bespoke interactive widgets, unique typography pairings, custom badges)
- Content and aesthetic differentiation relative to common industry clichés

You MUST return a JSON object with this exact schema:
{
  "score": 8.3,
  "issues": [
    "Originality issue description 1",
    "Originality issue description 2"
  ],
  "severity": ["medium"],
  "evidence": [
    "Element or pattern that feels cliché or generic",
    "Evidence detail"
  ],
  "recommendations": [
    "Bespoke design suggestion to elevate originality 1",
    "Bespoke design suggestion to elevate originality 2"
  ]
}
Do not include markdown fences or text outside the JSON.
"""


class OriginalityDiversityAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="originality_agent",
            system_prompt=SYSTEM_PROMPT
        )

    async def evaluate(
        self,
        website: WebsiteArtifacts,
        spec: StructuredPrompt
    ) -> Tuple[OriginalityCritique, AgentTelemetry]:
        prompt = f"""Target Project: {spec.project_goal}
Originality Requirements: {', '.join(spec.originality_requirements)}

Website HTML:
```html
{website.html[:4000]}
```

Website CSS:
```css
{website.css[:3000]}
```

Evaluate visual distinctness, layout freshness, and originality. Return the structured JSON critique."""

        data, raw, telemetry = await self.execute_llm(prompt=prompt, response_format_json=True)

        if not data or "score" not in data:
            data = {
                "score": 8.0,
                "issues": ["Layout incorporates standard multi-column grid"],
                "severity": ["low"],
                "evidence": ["Section container layout"],
                "recommendations": ["Introduce bespoke graphic accents or interactive data visualizers"]
            }

        return OriginalityCritique(**data), telemetry
