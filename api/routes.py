"""
REST API Routes for Web Design Generation & Inspection.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from config.settings import settings
from evaluation.metrics import MetricsEngine
from evaluation.static_analyzer import StaticAnalyzer
from orchestration.modes import SystemMode
from orchestration.orchestrator import Orchestrator
from orchestration.state import RunState, StructuredPrompt, WebsiteArtifacts
from sandbox.security import SandboxSecurity
from storage.database import Database
from storage.workspace import WorkspaceManager

router = APIRouter(prefix="/api", tags=["Web Design Generation API"])
orchestrator = Orchestrator()
workspace = WorkspaceManager(settings.workspace_dir)
db = Database(settings.database_url.replace("sqlite:///", ""))


class GenerateRequest(BaseModel):
    prompt: str = Field(description="Natural language request for website generation")
    system_mode: Optional[SystemMode] = Field(default=None, description="generator_only | general_critic | specialized_multi_agent")
    ablated_agents: Optional[List[str]] = Field(default=None, description="List of agents to ablate e.g. ['aesthetic', 'ethics']")
    max_iterations: Optional[int] = Field(default=None, ge=1, le=10)
    quality_threshold: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    framework: Optional[str] = Field(default="vanilla_gsap_lenis", description="vanilla_gsap_lenis | nextjs_react | tailwind_framer")
    animation_stack: Optional[str] = Field(default="gsap_lenis", description="gsap_lenis | framer_motion | css_svg")


class GenerateResponse(BaseModel):
    run_id: str
    status: str
    website_url: str
    composite_score: float
    scores: Dict[str, Any]
    iterations: int
    passed_gate: bool
    gate_reason: str


class RefineRequest(BaseModel):
    additional_feedback: Optional[str] = None


@router.post("/generate", response_model=GenerateResponse, summary="Generate website with multi-agent pipeline")
async def generate_website(req: GenerateRequest):
    """
    Generates a web design by executing prompt structuring, generation, multi-agent critique, and iterative refinement.
    """
    try:
        state: RunState = await orchestrator.run_pipeline(
            prompt=req.prompt,
            system_mode=req.system_mode,
            ablated_agents=req.ablated_agents,
            max_iterations=req.max_iterations,
            quality_threshold=req.quality_threshold,
            framework=req.framework or "vanilla_gsap_lenis",
            animation_stack=req.animation_stack or "gsap_lenis",
        )

        eval_m = state.evaluation
        scores = {}
        if eval_m:
            scores = {
                "aesthetic": eval_m.aesthetic_score,
                "accessibility": eval_m.accessibility_score,
                "usability": eval_m.usability_score,
                "ethics": eval_m.ethics_score,
                "originality": eval_m.originality_score,
                "composite": eval_m.composite_score,
            }

        return GenerateResponse(
            run_id=state.run_id,
            status=state.status,
            website_url=f"/api/preview/{state.run_id}/final",
            composite_score=eval_m.composite_score if eval_m else 0.0,
            scores=scores,
            iterations=state.current_iteration,
            passed_gate=eval_m.passed_gate if eval_m else False,
            gate_reason=eval_m.gate_reason if eval_m else "Completed",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/runs", summary="List historical runs")
async def list_runs(limit: int = Query(default=30, ge=1, le=100)):
    return db.list_runs(limit=limit)


@router.get("/run/{run_id}", summary="Get complete run state and artifacts")
async def get_run_details(run_id: str):
    run_data = workspace.load_run(run_id)
    if not run_data:
        db_data = db.get_run(run_id)
        if not db_data:
            raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")
        return db_data
    return run_data


@router.get("/run/{run_id}/evaluation", summary="Get evaluation report")
async def get_run_evaluation(run_id: str):
    run_data = workspace.load_run(run_id)
    if not run_data:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")
    return {
        "run_id": run_id,
        "evaluation": run_data.get("evaluation"),
        "agent_results": run_data.get("agent_results"),
        "aggregate_feedback": run_data.get("aggregate_feedback"),
        "total_latency_ms": run_data.get("total_latency_ms"),
        "total_token_usage": run_data.get("total_token_usage")
    }


@router.get("/run/{run_id}/iterations", summary="Get all iterations with code and critiques")
async def get_run_iterations(run_id: str):
    run_data = workspace.load_run(run_id)
    if not run_data:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")
    return {
        "run_id": run_id,
        "iterations_count": len(run_data.get("history", [])),
        "history": run_data.get("history", [])
    }


@router.get("/run/{run_id}/website", summary="Get current or final website code")
async def get_run_website(run_id: str, iteration: Optional[int] = None):
    run_dir = workspace.get_run_dir(run_id)
    
    if iteration is not None:
        target_dir = run_dir / f"iteration_{iteration:02d}" / "website"
    else:
        target_dir = run_dir / "final_website"
        if not target_dir.exists():
            target_dir = run_dir / "iteration_01" / "website"

    if not target_dir.exists():
        raise HTTPException(status_code=404, detail=f"Website artifacts not found for {run_id}")

    html = (target_dir / "index.html").read_text(encoding="utf-8") if (target_dir / "index.html").exists() else ""
    css = (target_dir / "styles.css").read_text(encoding="utf-8") if (target_dir / "styles.css").exists() else ""
    js = (target_dir / "script.js").read_text(encoding="utf-8") if (target_dir / "script.js").exists() else ""
    react_code = (target_dir / "page.tsx").read_text(encoding="utf-8") if (target_dir / "page.tsx").exists() else ""
    backend_schema = (target_dir / "backend_schema.ts").read_text(encoding="utf-8") if (target_dir / "backend_schema.ts").exists() else ""

    return {
        "run_id": run_id,
        "iteration": iteration or "final",
        "html": html,
        "css": css,
        "javascript": js,
        "react_code": react_code,
        "backend_schema": backend_schema
    }


@router.get("/preview/{run_id}/{target}", response_class=HTMLResponse, summary="Render sandboxed website in browser")
async def preview_website(run_id: str, target: str):
    """
    Renders the website for sandboxed preview. Injects inline CSS/JS and security headers.
    """
    run_dir = workspace.get_run_dir(run_id)
    if target == "final":
        site_dir = run_dir / "final_website"
        if not site_dir.exists():
            site_dir = run_dir / "iteration_01" / "website"
    else:
        try:
            it_num = int(target)
            site_dir = run_dir / f"iteration_{it_num:02d}" / "website"
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid target: must be 'final' or integer iteration.")

    if not site_dir.exists():
        raise HTTPException(status_code=404, detail="Preview not available.")

    html_file = site_dir / "index.html"
    css_file = site_dir / "styles.css"
    js_file = site_dir / "script.js"

    html = html_file.read_text(encoding="utf-8") if html_file.exists() else "<h1>Preview Not Found</h1>"
    css = css_file.read_text(encoding="utf-8") if css_file.exists() else ""
    js = js_file.read_text(encoding="utf-8") if js_file.exists() else ""

    # Bundle inline for independent sandboxed iframe rendering
    if "</head>" in html:
        bundle_head = f"<style>\n{css}\n</style>\n</head>"
        html = html.replace("</head>", bundle_head)
    elif "<body>" in html:
        html = f"<style>\n{css}\n</style>\n{html}"

    if "</body>" in html:
        bundle_body = f"<script>\n{js}\n</script>\n</body>"
        html = html.replace("</body>", bundle_body)
    else:
        html = f"{html}\n<script>\n{js}\n</script>"

    safe_html = SandboxSecurity.sanitize_preview_html(html)
    return HTMLResponse(content=safe_html, headers=SandboxSecurity.get_security_headers())
