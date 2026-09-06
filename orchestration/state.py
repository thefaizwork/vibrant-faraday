"""
Shared State and Data Models for Multi-Agent Web Design Generation.
Provides strongly-typed schemas for specifications, candidate websites, specialist critiques, and telemetry.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from providers.base import TokenUsage


# --- 1. Structured Prompt Specification ---
class StructuredPrompt(BaseModel):
    project_goal: str = Field(description="Core purpose and primary objective of the website")
    website_type: str = Field(description="Categorical type e.g. E-Commerce, SaaS, Portfolio, Landing")
    target_users: List[str] = Field(default_factory=list, description="Primary user personas and target audience")
    functional_requirements: List[str] = Field(default_factory=list, description="Interactive features, buttons, forms")
    visual_requirements: List[str] = Field(default_factory=list, description="Color palette, typography, visual tone")
    accessibility_requirements: List[str] = Field(default_factory=list, description="WCAG 2.1 AA targets, contrast, aria")
    usability_requirements: List[str] = Field(default_factory=list, description="Navigation, UX flow, CTA hierarchy")
    compliance_requirements: List[str] = Field(default_factory=list, description="Zero dark patterns, privacy, transparency")
    originality_requirements: List[str] = Field(default_factory=list, description="Distinctive visual and structural elements")
    technical_constraints: List[str] = Field(default_factory=list, description="HTML5/CSS3/Vanilla JS standards")
    content_requirements: List[str] = Field(default_factory=list, description="Copywriting, sections, disclosures")
    explicit_constraints: List[str] = Field(default_factory=list, description="Explicit boundaries and constraints")
    implicit_requirements: List[str] = Field(default_factory=list, description="Subtle UX expectations, smooth transitions")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Criteria for passing evaluation gate")


# --- 2. Generated Website Artifacts ---
class ComponentStructure(BaseModel):
    name: str
    role: str
    tag: str = "section"


class WebsiteArtifacts(BaseModel):
    html: str
    css: str
    javascript: str
    component_structure: List[ComponentStructure] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    design_rationale: str = ""
    framework: str = Field(default="vanilla_gsap_lenis", description="vanilla_gsap_lenis | nextjs_react | tailwind_framer")
    animation_stack: str = Field(default="gsap_lenis", description="gsap_lenis | framer_motion | css_svg")
    react_code: Optional[str] = Field(default=None, description="Complete Next.js 15+ / React TypeScript code bundle")
    backend_schema: Optional[str] = Field(default=None, description="Backend integration layer: types, API routes, client service")
    files: Dict[str, str] = Field(default_factory=dict, description="Virtual file tree of project files")



# --- 3. Specialized Agent Critique Schemas ---
class AestheticCritique(BaseModel):
    score: float = Field(ge=0.0, le=10.0, description="Aesthetic score from 0.0 to 10.0")
    issues: List[str] = Field(default_factory=list)
    severity: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class AccessibilityCritique(BaseModel):
    score: float = Field(ge=0.0, le=10.0, description="Accessibility score from 0.0 to 10.0")
    wcag_issues: List[str] = Field(default_factory=list)
    critical_issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    static_analysis: Optional[Dict[str, Any]] = None


class UsabilityCritique(BaseModel):
    score: float = Field(ge=0.0, le=10.0, description="Usability score from 0.0 to 10.0")
    issues: List[str] = Field(default_factory=list)
    severity: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class EthicsCritique(BaseModel):
    score: float = Field(ge=0.0, le=10.0, description="Ethics score from 0.0 to 10.0")
    dark_patterns_detected: List[str] = Field(default_factory=list)
    risk_level: str = Field(default="low", description="low, medium, high")
    evidence: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class OriginalityCritique(BaseModel):
    score: float = Field(ge=0.0, le=10.0, description="Originality score from 0.0 to 10.0")
    issues: List[str] = Field(default_factory=list)
    severity: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class GeneralCriticCritique(BaseModel):
    score: float = Field(ge=0.0, le=10.0, description="General evaluation score from 0.0 to 10.0")
    overall_feedback: str = ""
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


# --- 4. Feedback Aggregator & Refiner Schemas ---
class ConflictResolution(BaseModel):
    issue: str
    resolution: str


class FeedbackAggregate(BaseModel):
    priority_issues: List[str] = Field(default_factory=list)
    blocking_issues: List[str] = Field(default_factory=list)
    conflicts: List[Dict[str, str]] = Field(default_factory=list)
    recommended_changes: List[str] = Field(default_factory=list)
    preserve: List[str] = Field(default_factory=list)
    refinement_strategy: str = ""
    target_scores: Dict[str, float] = Field(default_factory=dict)


class IssueMapping(BaseModel):
    issue: str
    action_taken: str
    files_modified: List[str] = Field(default_factory=list)


class DesignRefinement(BaseModel):
    revised_html: str
    revised_css: str
    revised_js: str
    change_summary: str
    issue_mappings: List[IssueMapping] = Field(default_factory=list)


# --- 5. Evaluation Metrics & Telemetry ---
class EvaluationMetrics(BaseModel):
    aesthetic_score: Optional[float] = None
    accessibility_score: Optional[float] = None
    usability_score: Optional[float] = None
    ethics_score: Optional[float] = None
    originality_score: Optional[float] = None
    general_score: Optional[float] = None
    composite_score: float = 0.0
    wcag_pass_rate: float = 100.0
    dark_pattern_count: int = 0
    passed_gate: bool = False
    gate_reason: str = ""
    latency_ms: float = 0.0
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# --- 6. Iteration State & Run State ---
class IterationState(BaseModel):
    iteration_number: int
    website: WebsiteArtifacts
    critiques: Dict[str, Any] = Field(default_factory=dict)
    aggregate: Optional[FeedbackAggregate] = None
    refinement: Optional[DesignRefinement] = None
    evaluation: Optional[EvaluationMetrics] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RunState(BaseModel):
    run_id: str
    original_prompt: str
    structured_prompt: Optional[StructuredPrompt] = None
    system_mode: str = "specialized_multi_agent"
    ablated_agents: List[str] = Field(default_factory=list)
    current_iteration: int = 0
    website_version: str = "v1"
    agent_results: Dict[str, Any] = Field(default_factory=dict)
    aggregate_feedback: Optional[FeedbackAggregate] = None
    evaluation: Optional[EvaluationMetrics] = None
    history: List[IterationState] = Field(default_factory=list)
    status: str = "initialized" # initialized, in_progress, completed, failed
    error_message: Optional[str] = None
    total_latency_ms: float = 0.0
    total_token_usage: TokenUsage = Field(default_factory=TokenUsage)
    start_time: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    end_time: Optional[str] = None

    @property
    def final_website(self) -> Optional[WebsiteArtifacts]:
        """Returns the final iteration's website artifacts."""
        return self.history[-1].website if self.history else None

