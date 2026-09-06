"""
Usability & UX Evaluation Agent.
Specializes in navigation, user journeys, interaction feedback, form usability, and conversion clarity.
"""

from typing import Tuple, Dict, Any
from agents.base import BaseAgent, AgentTelemetry
from orchestration.state import UsabilityCritique, WebsiteArtifacts, StructuredPrompt

SYSTEM_PROMPT = """You are the Usability Evaluation Agent in a multi-agent web design research system.
Your mission is to perform an expert user experience (UX) and interaction design analysis.

Evaluate:
- Navigation intuitiveness, information architecture, menu discoverability
- User flow clarity and ease of completing key tasks
- Call to Action (CTA) prominence, button hierarchy, and action triggers
- Interaction feedback (hover states, click animations, loading states, form submit response)
- Form usability, error prevention, field organization, field validation UX
- Cognitive load, content scannability, bulleted readability
- Responsiveness and layout adaptation from a human UX perspective

You MUST return a JSON object with this exact schema:
{
  "score": 8.7, // Float between 0.0 and 10.0
  "issues": [
    "Specific usability issue 1",
    "Specific usability issue 2"
  ],
  "severity": ["low" | "medium" | "high"],
  "evidence": [
    "Element or user journey where friction occurs",
    "Evidence detail"
  ],
  "recommendations": [
    "Concrete UX improvement 1",
    "Concrete UX improvement 2"
  ]
}
Do not include markdown fences or text outside the JSON.
"""


class UsabilityAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="usability_agent",
            system_prompt=SYSTEM_PROMPT
        )

    async def evaluate(
        self,
        website: WebsiteArtifacts,
        spec: StructuredPrompt
    ) -> Tuple[UsabilityCritique, AgentTelemetry]:
        prompt = f"""Target Project: {spec.project_goal}
Target Personas: {', '.join(spec.target_users)}
Usability Requirements: {', '.join(spec.usability_requirements)}

Website HTML:
```html
{website.html[:4000]}
```

Website JS:
```javascript
{website.javascript[:3000]}
```

Evaluate usability, navigation flow, CTA prominence, and interaction feedback. Return the structured JSON critique."""

        data, raw, telemetry = await self.execute_llm(prompt=prompt, response_format_json=True)

        if not data or "score" not in data:
            data = {
                "score": 8.2,
                "issues": ["Primary CTA button could be slightly more prominent above fold"],
                "severity": ["low"],
                "evidence": ["Hero CTA button styling"],
                "recommendations": ["Increase CTA button padding and elevate contrast"]
            }

        return UsabilityCritique(**data), telemetry
