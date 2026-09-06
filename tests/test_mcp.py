"""
Integration tests for the Model Context Protocol (MCP) server tools.
"""

import pytest
from mcp_server.server import (
    generate_website,
    evaluate_website,
    refine_website,
    run_multi_agent_pipeline,
    get_run_status,
    get_evaluation_report,
    get_iteration_history,
)


@pytest.mark.asyncio
async def test_mcp_tools():
    # 1. Generate Website Tool
    res_gen = await generate_website(prompt="Create a sustainable clothing shop", max_iterations=1)
    assert "run_id" in res_gen
    assert res_gen["status"] == "completed"
    assert "composite_score" in res_gen
    run_id = res_gen["run_id"]

    # 2. Evaluate Website Tool
    sample_html = "<!DOCTYPE html><html><body><header><nav><a href='#'>Home</a></nav></header><main><h1>Title</h1></main></body></html>"
    res_eval = await evaluate_website(html=sample_html, prompt="Sustainable fashion")
    assert "composite_score" in res_eval
    assert "critiques" in res_eval

    # 3. Refine Website Tool
    res_refine = await refine_website(html=sample_html, feedback="Add shopping cart and increase contrast")
    assert "revised_html" in res_refine
    assert "change_summary" in res_refine

    # 4. Pipeline Run Tool
    res_pipe = await run_multi_agent_pipeline(prompt="SaaS analytics", system_mode="specialized_multi_agent", max_iterations=1)
    assert res_pipe["status"] == "completed"

    # 5. Status & History Tools
    status = await get_run_status(run_id)
    assert status["run_id"] == run_id

    report = await get_evaluation_report(run_id)
    assert "evaluation" in report

    history = await get_iteration_history(run_id)
    assert "iterations" in history
