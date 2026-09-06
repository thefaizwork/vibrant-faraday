"""
Integration tests for the multi-agent Orchestrator.
"""

import pytest
from orchestration.modes import SystemMode
from orchestration.orchestrator import Orchestrator
from storage.workspace import WorkspaceManager


@pytest.mark.asyncio
async def test_orchestrator_specialized_multi_agent():
    orchestrator = Orchestrator()
    state = await orchestrator.run_pipeline(
        prompt="Design a luxury sustainable shoe storefront",
        system_mode=SystemMode.SPECIALIZED_MULTI_AGENT,
        max_iterations=2,
    )
    assert state.status == "completed"
    assert state.current_iteration >= 1
    assert state.evaluation is not None
    assert state.evaluation.composite_score > 0.0
    assert len(state.history) >= 1

    # Verify disk artifacts
    run_dir = orchestrator.workspace.get_run_dir(state.run_id)
    assert (run_dir / "iteration_01" / "website" / "index.html").exists()
    assert (run_dir / "iteration_01" / "aggregate.json").exists()
    assert (run_dir / "final_website" / "index.html").exists()
    assert (run_dir / "final_report.json").exists()


@pytest.mark.asyncio
async def test_orchestrator_generator_only_mode():
    orchestrator = Orchestrator()
    state = await orchestrator.run_pipeline(
        prompt="Minimalist architect landing page",
        system_mode=SystemMode.GENERATOR_ONLY,
    )
    assert state.status == "completed"
    assert state.current_iteration == 1
    assert len(state.history) == 1


@pytest.mark.asyncio
async def test_orchestrator_general_critic_mode():
    orchestrator = Orchestrator()
    state = await orchestrator.run_pipeline(
        prompt="Fintech wealth manager dashboard",
        system_mode=SystemMode.GENERAL_CRITIC,
        max_iterations=1,
    )
    assert state.status == "completed"
    assert "general_critic" in state.agent_results


@pytest.mark.asyncio
async def test_orchestrator_ablation_mode():
    orchestrator = Orchestrator()
    # Ablate aesthetic and ethics
    state = await orchestrator.run_pipeline(
        prompt="Healthcare clinic appointment portal",
        system_mode=SystemMode.SPECIALIZED_MULTI_AGENT,
        ablated_agents=["aesthetic", "ethics"],
        max_iterations=1,
    )
    assert state.status == "completed"
    assert "aesthetic" not in state.agent_results
    assert "ethics" not in state.agent_results
    assert "accessibility" in state.agent_results
