"""
Prompt Structurer Agent.
Translates unstructured user requirements into a comprehensive 14-field research specification JSON.
"""

from typing import Dict, Any, Tuple
from agents.base import BaseAgent, AgentTelemetry
from orchestration.state import StructuredPrompt

SYSTEM_PROMPT = """You are the Prompt Structurer Agent in a multi-agent web design research system.
Your job is to analyze the user's natural-language request and convert it into a complete, formal, and strongly structured technical and design specification.

CRITICAL EXTRACTION GUIDELINES:
1. Extract any specific person name, brand name, studio name, or company mentioned (e.g., "Faizan Ahmad", "Aura Labs").
2. Set "website_type" accurately (e.g., "Video Editing Portfolio", "Creative Portfolio", "E-Commerce", "SaaS Landing Page", "Healthcare Portal", "Restaurant").
3. In "content_requirements", include real, punchy marketing headlines, slogans, and tailored section concepts (e.g., "Hero headline: Crafting High-Impact Cinematic Stories", "Showcase: Commercials, Music Videos, Documentary Color Grading, YouTube Edits"). NEVER echo the raw user prompt instructions as body copy.
4. In "functional_requirements", specify domain-specific interactive features (e.g. for a video editor: interactive video player/showreel modal, filterable project grid, editing software badges for DaVinci Resolve/Premiere/After Effects, project quote/rate estimator, booking inquiry form).

You MUST output ONLY a valid JSON object with the exact following schema:
{
  "project_goal": "Clear, concise statement of core project purpose",
  "website_type": "Specific website category (e.g., Video Editing Portfolio, E-Commerce, SaaS, Healthcare)",
  "target_users": ["List of target user personas and audiences"],
  "functional_requirements": ["List of required UI features, interactive elements, forms, widgets"],
  "visual_requirements": ["Color palette mood, typography styles, spacing, card aesthetics"],
  "accessibility_requirements": ["WCAG 2.1 AA targets, contrast standards, alt text, focus rings"],
  "usability_requirements": ["Navigation flow, CTA hierarchy, intuitive interaction design"],
  "compliance_requirements": ["Zero dark patterns, transparent disclosures, privacy compliance"],
  "originality_requirements": ["Distinctive layout choices, bespoke visual accents, avoiding clichés"],
  "technical_constraints": ["Pure HTML5, modular CSS3 variables, modern vanilla JavaScript (ES6+)"],
  "content_requirements": ["Headlines, value propositions, section copy, calls to action"],
  "explicit_constraints": ["Explicit boundaries or limitations stated by user"],
  "implicit_requirements": ["Unspoken best practices, responsiveness, smooth micro-interactions"],
  "acceptance_criteria": ["Measurable criteria for passing the evaluation gate"]
}
Do not include markdown fences or explanatory text outside the JSON object.
"""


class PromptStructurerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="prompt_structurer",
            system_prompt=SYSTEM_PROMPT
        )

    async def structure(self, user_prompt: str) -> Tuple[StructuredPrompt, AgentTelemetry]:
        """Convert natural language request to structured prompt."""
        prompt = f"User Request:\n\"\"\"\n{user_prompt}\n\"\"\"\n\nPlease structure this into the complete 14-field specification JSON."
        data, raw, telemetry = await self.execute_llm(prompt=prompt, response_format_json=True)
        
        if not data:
            # Fallback default structured prompt if LLM failed
            data = {
                "project_goal": f"Build a modern website based on: {user_prompt}",
                "website_type": "Interactive Web Platform",
                "target_users": ["General web users", "Target customer segment"],
                "functional_requirements": ["Navigation bar", "Hero section with CTA", "Feature showcase", "Contact/Signup form", "Footer"],
                "visual_requirements": ["Harmonious color palette", "Readable typography scale", "Consistent spacing"],
                "accessibility_requirements": ["WCAG 2.1 AA compliance", "High contrast", "Alt text on images", "Semantic HTML"],
                "usability_requirements": ["Clear navigation", "Prominent CTA", "Intuitive layout"],
                "compliance_requirements": ["No dark patterns", "Transparent terms", "Clear privacy practices"],
                "originality_requirements": ["Distinct visual identity", "Bespoke component structure"],
                "technical_constraints": ["Semantic HTML5", "Responsive CSS3", "Vanilla JavaScript"],
                "content_requirements": ["Engaging headline", "Product/Service details", "Clear calls to action"],
                "explicit_constraints": ["Fully self-contained in standard HTML/CSS/JS"],
                "implicit_requirements": ["Mobile-friendly responsiveness", "Fast rendering"],
                "acceptance_criteria": ["Composite score >= 8.0/10", "Zero blocking accessibility or ethics violations"]
            }

        return StructuredPrompt(**data), telemetry
