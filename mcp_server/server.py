"""
Model Context Protocol (MCP) Server for Multi-Agent Web Design System.
Exposes structured tools to AI clients (Claude, Cursor, OpenAI assistants) over standard MCP protocol.
"""

import json
from typing import Any, Dict, List, Optional

try:
    from mcp.server.mcpserver import MCPServer
    mcp = MCPServer("web-design-multi-agent")
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("web-design-multi-agent")
    except ImportError:
        # Fallback dummy decorator class if MCP is unavailable
        class DummyMCP:
            def tool(self):
                def decorator(fn):
                    return fn
                return decorator
            def run(self):
                print("MCP Server running in standalone mode.")
        mcp = DummyMCP()

from config.settings import settings
from evaluation.metrics import MetricsEngine
from evaluation.static_analyzer import StaticAnalyzer
from orchestration.modes import SystemMode
from orchestration.orchestrator import Orchestrator
from orchestration.state import WebsiteArtifacts
from storage.workspace import WorkspaceManager

orchestrator = Orchestrator()
workspace = WorkspaceManager(settings.workspace_dir)


@mcp.tool()
async def generate_website(prompt: str, max_iterations: int = 3) -> Dict[str, Any]:
    """
    Generate a complete, accessible, ethically-compliant web design from a natural language prompt.
    Runs the full multi-agent generation, evaluation, aggregation, and refinement loop.
    """
    state = await orchestrator.run_pipeline(prompt=prompt, max_iterations=max_iterations)
    final_site = state.history[-1].website if state.history else None
    
    return {
        "run_id": state.run_id,
        "status": state.status,
        "composite_score": state.evaluation.composite_score if state.evaluation else 0.0,
        "iterations_completed": state.current_iteration,
        "passed_gate": state.evaluation.passed_gate if state.evaluation else False,
        "html_snippet": final_site.html[:500] + "..." if final_site else "",
        "preview_url": f"http://localhost:8000/api/preview/{state.run_id}/final",
        "scores": {
            "aesthetic": state.evaluation.aesthetic_score if state.evaluation else None,
            "accessibility": state.evaluation.accessibility_score if state.evaluation else None,
            "usability": state.evaluation.usability_score if state.evaluation else None,
            "ethics": state.evaluation.ethics_score if state.evaluation else None,
            "originality": state.evaluation.originality_score if state.evaluation else None,
        }
    }


@mcp.tool()
async def evaluate_website(html: str, css: str = "", js: str = "", prompt: str = "Modern accessible web design") -> Dict[str, Any]:
    """
    Evaluate existing HTML/CSS/JS against 5 specialized design agents (Aesthetic, Accessibility, Usability, Ethics, Originality).
    """
    spec, _ = await orchestrator.structurer.structure(prompt)
    website = WebsiteArtifacts(html=html, css=css, javascript=js)
    active_agents = ["aesthetic", "accessibility", "usability", "ethics", "originality"]
    critiques, tokens = await orchestrator._run_critiques(website, spec, active_agents)
    
    static_res = StaticAnalyzer.analyze(html, css, js)
    metrics = MetricsEngine.compute_composite_metrics(
        agent_critiques=critiques,
        static_analysis=static_res,
        token_usage=tokens
    )

    return {
        "composite_score": metrics.composite_score,
        "wcag_pass_rate": metrics.wcag_pass_rate,
        "dark_patterns_detected": metrics.dark_pattern_count,
        "critiques": {k: (v.model_dump() if hasattr(v, "model_dump") else v) for k, v in critiques.items()},
        "static_checks": static_res
    }


@mcp.tool()
async def refine_website(html: str, css: str = "", js: str = "", feedback: str = "Improve contrast and user flow") -> Dict[str, Any]:
    """
    Refine existing website code by generating an aggregated action plan and applying surgical improvements.
    """
    spec, _ = await orchestrator.structurer.structure(feedback)
    website = WebsiteArtifacts(html=html, css=css, javascript=js)
    active_agents = ["aesthetic", "accessibility", "usability", "ethics", "originality"]
    critiques, _ = await orchestrator._run_critiques(website, spec, active_agents)
    agg, _ = await orchestrator.aggregator.aggregate(critiques, spec)
    refinement, _ = await orchestrator.refiner.refine(website, spec, agg)

    return {
        "revised_html": refinement.revised_html,
        "revised_css": refinement.revised_css,
        "revised_js": refinement.revised_js,
        "change_summary": refinement.change_summary,
        "issue_mappings": [m.model_dump() for m in refinement.issue_mappings],
    }


@mcp.tool()
async def run_multi_agent_pipeline(
    prompt: str,
    system_mode: str = "specialized_multi_agent",
    ablated_agents: Optional[List[str]] = None,
    max_iterations: int = 3,
    quality_threshold: float = 8.0,
) -> Dict[str, Any]:
    """
    Execute full pipeline with research controls (system_mode: generator_only, general_critic, specialized_multi_agent; ablated_agents).
    """
    mode = SystemMode(system_mode)
    state = await orchestrator.run_pipeline(
        prompt=prompt,
        system_mode=mode,
        ablated_agents=ablated_agents or [],
        max_iterations=max_iterations,
        quality_threshold=quality_threshold,
    )
    return {
        "run_id": state.run_id,
        "system_mode": state.system_mode,
        "status": state.status,
        "composite_score": state.evaluation.composite_score if state.evaluation else 0.0,
        "total_latency_ms": state.total_latency_ms,
        "total_tokens": state.total_token_usage.total_tokens,
        "iterations": state.current_iteration,
        "preview_url": f"http://localhost:8000/api/preview/{state.run_id}/final",
    }


@mcp.tool()
async def get_run_status(run_id: str) -> Dict[str, Any]:
    """
    Fetch the execution status and evaluation scores of a specific run ID.
    """
    run_data = workspace.load_run(run_id)
    if not run_data:
        return {"error": f"Run {run_id} not found"}
    return {
        "run_id": run_id,
        "status": run_data.get("status"),
        "system_mode": run_data.get("system_mode"),
        "current_iteration": run_data.get("current_iteration"),
        "evaluation": run_data.get("evaluation"),
        "total_latency_ms": run_data.get("total_latency_ms"),
    }


@mcp.tool()
async def get_evaluation_report(run_id: str) -> Dict[str, Any]:
    """
    Fetch comprehensive evaluation breakdown, specialist critiques, and gate decisions for a run.
    """
    run_data = workspace.load_run(run_id)
    if not run_data:
        return {"error": f"Run {run_id} not found"}
    return {
        "run_id": run_id,
        "evaluation": run_data.get("evaluation"),
        "agent_results": run_data.get("agent_results"),
        "aggregate_feedback": run_data.get("aggregate_feedback"),
    }


@mcp.tool()
async def get_iteration_history(run_id: str) -> Dict[str, Any]:
    """
    Fetch the complete history of iterations with change summaries, score trajectories, and code diffs.
    """
    run_data = workspace.load_run(run_id)
    if not run_data:
        return {"error": f"Run {run_id} not found"}
    return {
        "run_id": run_id,
        "iterations": [
            {
                "iteration": it.get("iteration_number"),
                "evaluation": it.get("evaluation"),
                "change_summary": it.get("refinement", {}).get("change_summary") if it.get("refinement") else "Initial generation",
                "critiques_summary": {k: v.get("score") for k, v in it.get("critiques", {}).items() if isinstance(v, dict)},
            }
            for it in run_data.get("history", [])
        ]
    }


if __name__ == "__main__":
    mcp.run()
