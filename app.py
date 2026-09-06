"""
Main Application CLI and Server Launcher.
Usage:
  python -m app --prompt "Create a modern sustainable fashion website"
  python -m app --server
  python -m app --mcp
"""

import argparse
import asyncio
import os
import sys
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from config.settings import settings, SystemMode
from orchestration.orchestrator import Orchestrator

console = Console()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Multi-Agent Web Design Generation & Evaluation System"
    )
    parser.add_argument(
        "--prompt",
        "-p",
        type=str,
        default="Create a modern e-commerce website for sustainable fashion.",
        help="Natural language prompt for website generation.",
    )
    parser.add_argument(
        "--mode",
        "-m",
        type=str,
        default="specialized_multi_agent",
        choices=["generator_only", "general_critic", "specialized_multi_agent"],
        help="Architecture mode to run.",
    )
    parser.add_argument(
        "--ablate",
        type=str,
        default="",
        help="Comma-separated list of agents to ablate.",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="Maximum refinement iterations.",
    )
    parser.add_argument(
        "--server",
        "-s",
        action="store_true",
        help="Start the FastAPI web server & interactive dashboard.",
    )
    parser.add_argument(
        "--mcp",
        action="store_true",
        help="Start the MCP (Model Context Protocol) server.",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Server host binding.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port binding.",
    )
    return parser.parse_args()


async def run_cli_pipeline(args):
    console.print(Panel.fit(
        "[bold cyan]Large-Scale Multi-Agent System for Aesthetic and Compliance-Aware Web Design[/bold cyan]\n"
        f"[dim]Mode:[/dim] [green]{args.mode}[/green] | [dim]Max Iterations:[/dim] [yellow]{args.max_iterations}[/yellow]",
        border_style="cyan"
    ))

    console.print(f"\n[bold yellow]User Prompt:[/bold yellow] \"{args.prompt}\"\n")

    orchestrator = Orchestrator()
    ablated = [a.strip() for a in args.ablate.split(",") if a.strip()]
    mode = SystemMode(args.mode)

    with console.status("[bold green]Executing multi-agent generation & evaluation loop...[/bold green]"):
        state = await orchestrator.run_pipeline(
            prompt=args.prompt,
            system_mode=mode,
            ablated_agents=ablated,
            max_iterations=args.max_iterations,
        )

    console.print(f"\n[bold green][OK] Execution Completed![/bold green] (Run ID: [bold]{state.run_id}[/bold])")
    console.print(f"Total Iterations: [cyan]{state.current_iteration}[/cyan] | Latency: [cyan]{state.total_latency_ms:.1f}ms[/cyan] | Status: [bold]{state.status}[/bold]")

    ev = state.evaluation
    if ev:
        table = Table(title="Final Multi-Agent Evaluation Metrics", border_style="cyan")
        table.add_column("Dimension / Metric", style="bold")
        table.add_column("Score / Result", justify="right", style="cyan")

        table.add_row("Composite Quality Score", f"{ev.composite_score:.2f} / 10.0")
        if ev.aesthetic_score is not None:
            table.add_row("Aesthetic Agent Score", f"{ev.aesthetic_score:.2f} / 10.0")
        if ev.accessibility_score is not None:
            table.add_row("Accessibility Agent Score", f"{ev.accessibility_score:.2f} / 10.0")
        if ev.usability_score is not None:
            table.add_row("Usability Agent Score", f"{ev.usability_score:.2f} / 10.0")
        if ev.ethics_score is not None:
            table.add_row("Ethics & Compliance Score", f"{ev.ethics_score:.2f} / 10.0")
        if ev.originality_score is not None:
            table.add_row("Originality & Diversity Score", f"{ev.originality_score:.2f} / 10.0")
        if ev.general_score is not None:
            table.add_row("General Critic Score", f"{ev.general_score:.2f} / 10.0")

        table.add_row("WCAG Pass Rate", f"{ev.wcag_pass_rate:.1f}%")
        table.add_row("Dark Patterns Detected", f"{ev.dark_pattern_count}")
        table.add_row("Quality Gate Passed", f"[{'green' if ev.passed_gate else 'yellow'}]{ev.passed_gate}[/]")
        table.add_row("Gate Decision", f"{ev.gate_reason}")

        console.print(table)

    run_dir = orchestrator.workspace.get_run_dir(state.run_id)
    console.print(f"\n[bold cyan]Artifacts Saved to:[/bold cyan] file:///{run_dir.resolve().as_posix()}/")
    console.print(f"  * HTML: file:///{run_dir.resolve().as_posix()}/final_website/index.html")
    console.print(f"  * Report: file:///{run_dir.resolve().as_posix()}/final_report.json")
    console.print(f"  * Telemetry: file:///{run_dir.resolve().as_posix()}/telemetry.jsonl\n")


def main():
    args = parse_args()

    if args.server:
        console.print(f"[bold green]Starting Web Design System Server at http://{args.host}:{args.port}[/bold green]")
        uvicorn.run("api.app:app", host=args.host, port=args.port, reload=False)
    elif args.mcp:
        from mcp_server.server import mcp
        console.print("[bold green]Starting MCP Server on stdio...[/bold green]")
        mcp.run()
    else:
        asyncio.run(run_cli_pipeline(args))


if __name__ == "__main__":
    main()
