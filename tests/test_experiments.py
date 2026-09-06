"""
Integration tests for the research experiment benchmark framework.
"""

from pathlib import Path
import pytest
from experiments.runner import ExperimentRunner
from orchestration.modes import SystemMode


@pytest.mark.asyncio
async def test_experiment_runner_benchmark():
    runner = ExperimentRunner(output_dir=Path("./runs/test_results"))
    res = await runner.run_benchmark(
        benchmark_file=Path("./datasets/benchmark.json"),
        system_mode=SystemMode.SPECIALIZED_MULTI_AGENT,
        max_tasks=1,
        max_iterations=1,
    )
    assert "summary" in res
    assert res["summary"]["total_tasks"] == 1
    assert res["summary"]["mean_composite_score"] > 0.0
    assert Path(res["json_file"]).exists()
    assert Path(res["csv_file"]).exists()
