"""
Benchmark Experiment Runner CLI.
Investigates whether multiple specialized agents outperform single-generator and general-critic baselines.
"""

import argparse
import asyncio
from pathlib import Path
from typing import List, Optional
from experiments.analysis import ExperimentAnalyzer
from experiments.runner import ExperimentRunner
from orchestration.modes import SystemMode


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run web design multi-agent research benchmark experiments."
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="specialized_multi_agent",
        choices=["generator_only", "general_critic", "specialized_multi_agent"],
        help="System architecture mode to test.",
    )
    parser.add_argument(
        "--ablate",
        type=str,
        default="",
        help="Comma-separated list of agents to ablate (e.g., 'aesthetic,ethics').",
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        default="./datasets/benchmark.json",
        help="Path to benchmark JSON dataset.",
    )
    parser.add_argument(
        "--tasks",
        type=int,
        default=None,
        help="Limit number of benchmark tasks to run.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./results",
        help="Directory to save experiment results.",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="Maximum iterations per task.",
    )
    parser.add_argument(
        "--all-modes",
        action="store_true",
        help="Run comprehensive sweep across all 3 baseline modes and output comparative analysis.",
    )
    return parser.parse_args()


async def main():
    args = parse_args()
    runner = ExperimentRunner(output_dir=Path(args.output))
    bench_file = Path(args.benchmark)

    if args.all_modes:
        print("\n=======================================================")
        print("[*] RUNNING COMPLETE 3-MODE RESEARCH BENCHMARK SWEEP")
        print("=======================================================\n")

        modes = [
            SystemMode.GENERATOR_ONLY,
            SystemMode.GENERAL_CRITIC,
            SystemMode.SPECIALIZED_MULTI_AGENT,
        ]
        json_files = []

        for m in modes:
            res = await runner.run_benchmark(
                benchmark_file=bench_file,
                system_mode=m,
                max_tasks=args.tasks,
                max_iterations=args.max_iterations,
            )
            json_files.append(Path(res["json_file"]))

        comparison_table = ExperimentAnalyzer.generate_comparison_table(json_files)
        print("\n" + comparison_table)
        
        # Save comparison report
        report_path = Path(args.output) / "comparative_study_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(comparison_table)
        print(f"[+] Full comparative report saved to: {report_path}\n")

    else:
        ablated = [a.strip() for a in args.ablate.split(",") if a.strip()]
        mode = SystemMode(args.mode)
        await runner.run_benchmark(
            benchmark_file=bench_file,
            system_mode=mode,
            ablated_agents=ablated,
            max_tasks=args.tasks,
            max_iterations=args.max_iterations,
        )


if __name__ == "__main__":
    asyncio.run(main())
