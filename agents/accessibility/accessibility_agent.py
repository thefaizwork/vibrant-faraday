"""
Accessibility Evaluation Agent.
Combines deterministic DOM/WCAG rules with semantic LLM evaluation of accessibility.
"""

from typing import Tuple, Dict, Any
from agents.base import BaseAgent, AgentTelemetry
from evaluation.static_analyzer import StaticAnalyzer
from orchestration.state import AccessibilityCritique, WebsiteArtifacts, StructuredPrompt

SYSTEM_PROMPT = """You are the Accessibility Evaluation Agent in a multi-agent web design research system.
Your mission is to perform an in-depth accessibility review adhering to WCAG 2.1 AA standards.

Evaluate:
- WCAG 2.1 AA issues (color contrast, text resizing, reflow)
- Color contrast between foreground text and backgrounds (min 4.5:1 for normal text, 3:1 for large text)
- Image alt text descriptiveness and meaningful non-text content representations
- Semantic HTML (proper headings order h1->h2->h3, list structures, tables, form controls)
- Keyboard accessibility, tab navigation flow, visible focus states (outline/focus-visible)
- Form control labels, error announcements, fieldsets, aria-required
- Screen reader announcements (aria-live, role, aria-label, aria-expanded)

You MUST return a JSON object with this exact schema:
{
  "score": 8.8,
  "wcag_issues": [
    "WCAG issue description 1",
    "WCAG issue description 2"
  ],
  "critical_issues": [
    "Critical blocking accessibility failure (if any, e.g. unlabelled form submit or missing alt)"
  ],
  "recommendations": [
    "Concrete remediation step 1",
    "Concrete remediation step 2"
  ]
}
Do not include markdown fences or text outside the JSON.
"""


class AccessibilityAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="accessibility_agent",
            system_prompt=SYSTEM_PROMPT
        )

    async def evaluate(
        self,
        website: WebsiteArtifacts,
        spec: StructuredPrompt
    ) -> Tuple[AccessibilityCritique, AgentTelemetry]:
        # 1. Run deterministic static analysis first
        static_res = StaticAnalyzer.analyze(website.html, website.css, website.javascript)

        prompt = f"""Target Project: {spec.project_goal}
Accessibility Requirements: {', '.join(spec.accessibility_requirements)}

Deterministic Static Analysis Findings:
- Static WCAG Score: {static_res['wcag_score']}/10.0
- Critical Issues Detected: {static_res['critical_issues']}
- WCAG Issues Detected: {static_res['wcag_issues']}

Website HTML:
```html
{website.html[:4000]}
```

Website CSS:
```css
{website.css[:3000]}
```

Evaluate semantic accessibility, keyboard navigation, focus indicators, and WCAG 2.1 AA conformance. Combine your findings with the static analysis."""

        data, raw, telemetry = await self.execute_llm(prompt=prompt, response_format_json=True)

        if not data or "score" not in data:
            data = {
                "score": static_res["wcag_score"],
                "wcag_issues": static_res["wcag_issues"],
                "critical_issues": static_res["critical_issues"],
                "recommendations": ["Ensure visible :focus-visible outlines on all interactive controls", "Verify alt text on all images"]
            }

        # Merge any static critical issues
        all_crit = list(set(data.get("critical_issues", []) + static_res["critical_issues"]))
        all_wcag = list(set(data.get("wcag_issues", []) + static_res["wcag_issues"]))
        
        critique = AccessibilityCritique(
            score=data.get("score", static_res["wcag_score"]),
            wcag_issues=all_wcag,
            critical_issues=all_crit,
            recommendations=data.get("recommendations", []),
            static_analysis=static_res
        )

        return critique, telemetry
