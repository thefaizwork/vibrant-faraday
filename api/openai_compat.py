"""
OpenAI-Compatible & Direct Integration API Endpoints.
Allows any standard external AI client, agent or proxy to interact with the multi-agent design system.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from orchestration.orchestrator import Orchestrator
from orchestration.state import (
    FeedbackAggregate,
    StructuredPrompt,
    WebsiteArtifacts,
)

router = APIRouter(prefix="/v1", tags=["OpenAI / Universal Agent Interface"])
orchestrator = Orchestrator()


class UniversalGenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = "multi-agent-web-v1"
    system_mode: Optional[str] = "specialized_multi_agent"
    max_iterations: Optional[int] = 3


class UniversalEvaluateRequest(BaseModel):
    html: str
    css: Optional[str] = ""
    javascript: Optional[str] = ""
    prompt: Optional[str] = "Evaluate modern accessible web design"


class UniversalRefineRequest(BaseModel):
    html: str
    css: Optional[str] = ""
    javascript: Optional[str] = ""
    feedback: Optional[str] = "Improve visual contrast and responsiveness"


@router.post("/generate", summary="Universal generation endpoint")
async def universal_generate(req: UniversalGenerateRequest):
    """
    Generates a website using the multi-agent system and returns predictable structured JSON.
    """
    try:
        state = await orchestrator.run_pipeline(
            prompt=req.prompt,
            max_iterations=req.max_iterations,
        )
        final_website = state.history[-1].website if state.history else None
        
        return {
            "id": state.run_id,
            "object": "web_generation",
            "status": state.status,
            "website": {
                "html": final_website.html if final_website else "",
                "css": final_website.css if final_website else "",
                "javascript": final_website.javascript if final_website else "",
            },
            "evaluation": state.evaluation.model_dump() if state.evaluation else {},
            "iterations_count": state.current_iteration,
            "usage": state.total_token_usage.model_dump(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate", summary="Universal evaluation endpoint")
async def universal_evaluate(req: UniversalEvaluateRequest):
    """
    Runs multi-agent critique suite on externally provided HTML/CSS/JS.
    """
    try:
        spec, _ = await orchestrator.structurer.structure(req.prompt)
        website = WebsiteArtifacts(
            html=req.html,
            css=req.css or "",
            javascript=req.javascript or ""
        )
        active_agents = ["aesthetic", "accessibility", "usability", "ethics", "originality"]
        critiques, tokens = await orchestrator._run_critiques(website, spec, active_agents)
        
        from evaluation.metrics import MetricsEngine
        from evaluation.static_analyzer import StaticAnalyzer
        static_res = StaticAnalyzer.analyze(website.html, website.css, website.javascript)
        metrics = MetricsEngine.compute_composite_metrics(
            agent_critiques=critiques,
            static_analysis=static_res,
            token_usage=tokens
        )

        return {
            "object": "web_evaluation",
            "metrics": metrics.model_dump(),
            "critiques": {k: v.model_dump() if hasattr(v, "model_dump") else v for k, v in critiques.items()},
            "static_analysis": static_res,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refine", summary="Universal refinement endpoint")
async def universal_refine(req: UniversalRefineRequest):
    """
    Evaluates and refines existing HTML/CSS/JS.
    """
    try:
        spec, _ = await orchestrator.structurer.structure(req.feedback or "General web polish")
        website = WebsiteArtifacts(
            html=req.html,
            css=req.css or "",
            javascript=req.javascript or ""
        )
        active_agents = ["aesthetic", "accessibility", "usability", "ethics", "originality"]
        critiques, _ = await orchestrator._run_critiques(website, spec, active_agents)
        agg, _ = await orchestrator.aggregator.aggregate(critiques, spec)
        refinement, tel = await orchestrator.refiner.refine(website, spec, agg)

        return {
            "object": "web_refinement",
            "revised_website": {
                "html": refinement.revised_html,
                "css": refinement.revised_css,
                "javascript": refinement.revised_js,
            },
            "change_summary": refinement.change_summary,
            "issue_mappings": [m.model_dump() for m in refinement.issue_mappings],
            "aggregate_plan": agg.model_dump(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
