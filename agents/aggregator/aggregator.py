"""
Feedback Aggregator Agent.
Synthesizes, resolves conflicts, prioritizes issues, and formulates an actionable refinement plan.
"""

import json
from typing import Any, Dict, List, Tuple
from agents.base import BaseAgent, AgentTelemetry
from orchestration.state import FeedbackAggregate, StructuredPrompt

SYSTEM_PROMPT = """You are the Feedback Aggregator Agent in a multi-agent web design research system.
Your mission is to analyze all incoming critiques from specialized evaluation agents, detect any conflicting advice, prioritize actionable fixes, identify blocking vs non-blocking issues, and construct a precise, high-impact refinement plan.

IMPORTANT: You must NOT rewrite the website code yourself. You produce prioritized instructions, conflict resolutions, and preservation directives for the Design Refiner.

You MUST return a JSON object with this exact schema:
{
  "priority_issues": [
    "High priority issue 1 with clear rationale",
    "High priority issue 2 with clear rationale"
  ],
  "blocking_issues": [
    "Critical blocking issue 1 (e.g., WCAG failure, severe dark pattern) that MUST be fixed"
  ],
  "conflicts": [
    {
      "issue": "Description of conflicting recommendation between agents (e.g. aesthetic minimalism vs accessibility contrast)",
      "resolution": "Specific balanced resolution directive (e.g. increase border contrast to 4.5:1 while keeping minimal styling)"
    }
  ],
  "recommended_changes": [
    "Concrete actionable change 1 for CSS/HTML/JS",
    "Concrete actionable change 2 for CSS/HTML/JS"
  ],
  "preserve": [
    "Core feature, aesthetic style, or functionality that is working exceptionally well and MUST NOT be broken"
  ],
  "refinement_strategy": "A concise executive summary of the refinement roadmap for this iteration",
  "target_scores": {
    "aesthetic": 8.5,
    "accessibility": 9.0,
    "usability": 8.8,
    "ethics": 9.5,
    "originality": 8.5
  }
}
Do not include markdown fences or text outside the JSON.
"""


class FeedbackAggregatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="aggregator",
            system_prompt=SYSTEM_PROMPT
        )

    async def aggregate(
        self,
        critiques: Dict[str, Any],
        spec: StructuredPrompt
    ) -> Tuple[FeedbackAggregate, AgentTelemetry]:
        serialized_critiques = {
            k: (v.model_dump() if hasattr(v, "model_dump") else v)
            for k, v in critiques.items()
        }
        prompt = f"""Project Goal: {spec.project_goal}

Agent Critiques to Aggregate:
\"\"\"
{json.dumps(serialized_critiques, indent=2)}
\"\"\"

Synthesize all critiques, resolve any conflicting recommendations, identify blocking items, and output the structured JSON refinement plan."""

        data, raw, telemetry = await self.execute_llm(prompt=prompt, response_format_json=True)

        if not data or "priority_issues" not in data:
            # Fallback aggregation
            data = {
                "priority_issues": ["Improve contrast and interactive feedback"],
                "blocking_issues": [],
                "conflicts": [],
                "recommended_changes": ["Update CSS contrast and enhance button feedback"],
                "preserve": ["Semantic HTML structure", "Core layout and typography"],
                "refinement_strategy": "Targeted styling and accessibility enhancements.",
                "target_scores": {"aesthetic": 8.5, "accessibility": 9.0, "usability": 8.5, "ethics": 9.5, "originality": 8.0}
            }

        return FeedbackAggregate(**data), telemetry
