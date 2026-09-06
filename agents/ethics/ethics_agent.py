"""
Ethics & Compliance Evaluation Agent.
Specializes in dark pattern detection, deceptive interactions, forced continuity, and privacy/transparency compliance.
"""

from typing import Tuple, Dict, Any
from agents.base import BaseAgent, AgentTelemetry
from evaluation.static_analyzer import StaticAnalyzer
from orchestration.state import EthicsCritique, WebsiteArtifacts, StructuredPrompt

SYSTEM_PROMPT = """You are the Ethics & Compliance Evaluation Agent in a multi-agent web design research system.
Your mission is to perform a rigorous ethical audit and dark-pattern detection on the candidate web design.

Evaluate:
- Dark patterns & deceptive UI (fake urgency timers, phantom stock counts, artificial scarcity)
- Manipulative choice architectures (confirm-shaming, pre-selected checkboxes, hidden opt-outs)
- Sneaking & hidden costs (unclear pricing, hidden recurring subscriptions, misleading fees)
- Forced continuity / obstruction (difficult cancellation, obfuscated terms)
- Misleading calls to action or disguised advertisements
- Privacy & data transparency (clear consent, respectful data policies, no deceptive tracking triggers)

Note: Do not make unsupported legal claims; focus on ethical design standards, FTC deceptive design principles, and transparent UX.

You MUST return a JSON object with this exact schema:
{
  "score": 9.5,
  "dark_patterns_detected": [
    "Identified dark pattern 1 (if any)",
    "Identified dark pattern 2 (if any)"
  ],
  "risk_level": "low",
  "evidence": [
    "Specific copy or UI element demonstrating the concern",
    "Evidence detail"
  ],
  "recommendations": [
    "Ethical remediation recommendation 1",
    "Ethical remediation recommendation 2"
  ]
}
Do not include markdown fences or text outside the JSON.
"""


class EthicsComplianceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ethics_agent",
            system_prompt=SYSTEM_PROMPT
        )

    async def evaluate(
        self,
        website: WebsiteArtifacts,
        spec: StructuredPrompt
    ) -> Tuple[EthicsCritique, AgentTelemetry]:
        # 1. Run deterministic static dark pattern analysis first
        static_res = StaticAnalyzer.analyze(website.html, website.css, website.javascript)
        static_dark_patterns = static_res.get("dark_patterns", [])

        prompt = f"""Target Project: {spec.project_goal}
Compliance Requirements: {', '.join(spec.compliance_requirements)}

Deterministic Rule Heuristic Flags: {static_dark_patterns if static_dark_patterns else 'None detected by rule scanner.'}

Website HTML:
```html
{website.html[:4500]}
```

Website JS:
```javascript
{website.javascript[:2500]}
```

Perform a thorough ethical audit. Check for manipulative copy, fake urgency, hidden costs, or confirm-shaming. Return the structured JSON critique."""

        data, raw, telemetry = await self.execute_llm(prompt=prompt, response_format_json=True)

        if not data or "score" not in data:
            data = {
                "score": static_res.get("ethics_static_score", 9.0),
                "dark_patterns_detected": static_dark_patterns,
                "risk_level": "low" if not static_dark_patterns else "medium",
                "evidence": ["DOM inspection"],
                "recommendations": ["Ensure all disclosures and privacy notices remain transparent"]
            }

        # Merge static findings
        all_dark_patterns = list(set(data.get("dark_patterns_detected", []) + static_dark_patterns))
        risk_level = data.get("risk_level", "low")
        if all_dark_patterns and risk_level == "low":
            risk_level = "medium"

        critique = EthicsCritique(
            score=data.get("score", 9.0),
            dark_patterns_detected=all_dark_patterns,
            risk_level=risk_level,
            evidence=data.get("evidence", []),
            recommendations=data.get("recommendations", [])
        )

        return critique, telemetry
