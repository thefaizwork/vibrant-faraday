"""
Experiment Execution Engine for Multi-Agent Web Design Research.
"""

import asyncio
import csv
import json
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
from orchestration.modes import SystemMode
from orchestration.orchestrator import Orchestrator
from orchestration.state import RunState


class ExperimentRunner:
    def __init__(self, output_dir: Path = Path("./results")):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.orchestrator = Orchestrator()

    async def run_benchmark(
        self,
        benchmark_file: Path = Path("./datasets/benchmark.json"),
        system_mode: SystemMode = SystemMode.SPECIALIZED_MULTI_AGENT,
        ablated_agents: Optional[List[str]] = None,
        max_tasks: Optional[int] = None,
        max_iterations: int = 3,
        quality_threshold: float = 8.0,
    ) -> Dict[str, Any]:
        """
        Runs experiment across the benchmark suite and records full metrics.
        """
        with open(benchmark_file, "r", encoding="utf-8") as f:
            tasks = json.load(f)

        if max_tasks:
            tasks = tasks[:max_tasks]

        experiment_id = f"exp_{system_mode.value}_{time.strftime('%Y%m%d_%H%M%S')}"
        if ablated_agents:
            experiment_id += f"_ablate_{'_'.join(ablated_agents)}"

        print(f"\n=======================================================")
        print(f"[*] Starting Benchmark Experiment: {experiment_id}")
        print(f"Mode: {system_mode.value} | Tasks: {len(tasks)} | Ablated: {ablated_agents or 'None'}")
        print(f"=======================================================\n")

        results = []
        for idx, task in enumerate(tasks, 1):
            task_id = task.get("id", f"task_{idx}")
            prompt = task.get("prompt", "")
            print(f"[{idx}/{len(tasks)}] Running task: {task_id} ...")

            start_t = time.perf_counter()
            state: RunState = await self.orchestrator.run_pipeline(
                prompt=prompt,
                system_mode=system_mode,
                ablated_agents=ablated_agents,
                max_iterations=max_iterations,
                quality_threshold=quality_threshold,
            )
            elapsed = time.perf_counter() - start_t

            ev = state.evaluation
            record = {
                "experiment_id": experiment_id,
                "task_id": task_id,
                "website_type": task.get("website_type", "General"),
                "system_mode": system_mode.value,
                "ablated_agents": ",".join(ablated_agents or []),
                "run_id": state.run_id,
                "status": state.status,
                "iterations": state.current_iteration,
                "passed_gate": ev.passed_gate if ev else False,
                "composite_score": ev.composite_score if ev else 0.0,
                "aesthetic_score": ev.aesthetic_score if ev else None,
                "accessibility_score": ev.accessibility_score if ev else None,
                "usability_score": ev.usability_score if ev else None,
                "ethics_score": ev.ethics_score if ev else None,
                "originality_score": ev.originality_score if ev else None,
                "general_score": ev.general_score if ev else None,
                "wcag_pass_rate": ev.wcag_pass_rate if ev else 100.0,
                "dark_pattern_count": ev.dark_pattern_count if ev else 0,
                "total_tokens": state.total_token_usage.total_tokens,
                "estimated_cost_usd": state.total_token_usage.estimated_cost_usd,
                "latency_ms": state.total_latency_ms,
                "elapsed_sec": round(elapsed, 2),
            }
            results.append(record)
            print(f"    [OK] Done in {elapsed:.1f}s | Score: {record['composite_score']} | Iters: {record['iterations']}")

        # Compute summary aggregate statistics
        summary = self._compute_summary(results, experiment_id, system_mode.value, ablated_agents)

        # Save files
        json_out = self.output_dir / f"{experiment_id}.json"
        csv_out = self.output_dir / f"{experiment_id}.csv"

        with open(json_out, "w", encoding="utf-8") as f:
            json.dump({"summary": summary, "results": results}, f, indent=2)

        if results:
            keys = list(results[0].keys())
            with open(csv_out, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(results)

        print(f"\n[+] Experiment completed! Results saved to:")
        print(f"   JSON: {json_out}")
        print(f"   CSV:  {csv_out}\n")

        return {"summary": summary, "results": results, "json_file": str(json_out), "csv_file": str(csv_out)}

    def _compute_summary(
        self,
        results: List[Dict[str, Any]],
        experiment_id: str,
        mode: str,
        ablated: Optional[List[str]]
    ) -> Dict[str, Any]:
        if not results:
            return {}

        n = len(results)
        avg = lambda key: round(sum(r[key] for r in results if r.get(key) is not None) / max(1, len([r for r in results if r.get(key) is not None])), 2)

        return {
            "experiment_id": experiment_id,
            "system_mode": mode,
            "ablated_agents": ablated or [],
            "total_tasks": n,
            "mean_composite_score": avg("composite_score"),
            "mean_aesthetic_score": avg("aesthetic_score"),
            "mean_accessibility_score": avg("accessibility_score"),
            "mean_usability_score": avg("usability_score"),
            "mean_ethics_score": avg("ethics_score"),
            "mean_originality_score": avg("originality_score"),
            "mean_wcag_pass_rate": avg("wcag_pass_rate"),
            "total_dark_patterns": sum(r.get("dark_pattern_count", 0) for r in results),
            "mean_iterations": avg("iterations"),
            "mean_latency_ms": avg("latency_ms"),
            "total_tokens": sum(r.get("total_tokens", 0) for r in results),
            "total_cost_usd": round(sum(r.get("estimated_cost_usd", 0.0) for r in results), 4),
        }
