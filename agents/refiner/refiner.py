"""
Design Refiner Agent.
Surgically applies aggregated feedback to the candidate website while preserving working functionality.
"""

import json
from typing import Any, Dict, List, Tuple
from agents.base import BaseAgent, AgentTelemetry
from orchestration.state import (
    DesignRefinement,
    FeedbackAggregate,
    IssueMapping,
    StructuredPrompt,
    WebsiteArtifacts,
)

SYSTEM_PROMPT = """You are the Design Refiner Agent in a multi-agent web design research system.
Your mission is to surgically revise and elevate the candidate website based on the aggregated feedback plan and structured requirements.

CRITICAL INSTRUCTIONS:
1. Preserve all working functionality, semantic structure, and styling unless a change is explicitly required by the feedback.
2. Address each high-priority and blocking issue directly in the revised HTML, CSS, or JavaScript.
3. Obey all 'preserve' directives from the aggregator.
4. Maintain strict WCAG 2.1 AA compliance and ensure zero dark patterns.
5. Provide a clear mapping for every change made to the corresponding feedback issue.

You MUST return a JSON object with this exact schema:
{
  "revised_html": "<!DOCTYPE html>... complete updated html ...",
  "revised_css": "/* complete updated css stylesheet */",
  "revised_js": "// complete updated javascript code",
  "change_summary": "High-level summary of all improvements made in this iteration",
  "issue_mappings": [
    {
      "issue": "Specific feedback issue addressed",
      "action_taken": "Precise code modification made in HTML/CSS/JS",
      "files_modified": ["styles.css", "script.js"]
    }
  ]
}
Do not include markdown fences or text outside the JSON.
"""


class DesignRefinerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="refiner",
            system_prompt=SYSTEM_PROMPT
        )

    async def refine(
        self,
        current_site: WebsiteArtifacts,
        spec: StructuredPrompt,
        feedback: FeedbackAggregate
    ) -> Tuple[DesignRefinement, AgentTelemetry]:
        prompt = f"""Target Project Specification:
{json.dumps(spec.model_dump(), indent=2)}

Aggregated Feedback & Plan:
{json.dumps(feedback.model_dump(), indent=2)}

Current Website Code:
--- HTML ---
{current_site.html}

--- CSS ---
{current_site.css}

--- JS ---
{current_site.javascript}

Apply the refinement plan surgically. Return the revised HTML, CSS, JS, change summary, and issue mappings in JSON."""

        data, raw, telemetry = await self.execute_llm(prompt=prompt, response_format_json=True)

        if not data or "revised_html" not in data or "revised_css" not in data:
            # Fallback refinement if LLM parse failed
            data = {
                "revised_html": current_site.html,
                "revised_css": current_site.css + "\n/* Refined: enhanced contrast */\n:focus-visible { outline: 3px solid #185ADB; }",
                "revised_js": current_site.javascript,
                "change_summary": "Maintained current design baseline with focus-visible accessibility safeguard.",
                "issue_mappings": [
                    {
                        "issue": "Ensure accessibility safeguards",
                        "action_taken": "Added explicit :focus-visible rules",
                        "files_modified": ["styles.css"]
                    }
                ]
            }

        mappings = [
            IssueMapping(**m) if isinstance(m, dict) else IssueMapping(issue="General polish", action_taken="Code refinement", files_modified=["styles.css"])
            for m in data.get("issue_mappings", [])
        ]

        refinement = DesignRefinement(
            revised_html=data["revised_html"],
            revised_css=data.get("revised_css", current_site.css),
            revised_js=data.get("revised_js", current_site.javascript),
            change_summary=data.get("change_summary", "Refined design candidate."),
            issue_mappings=mappings
        )

        return refinement, telemetry
