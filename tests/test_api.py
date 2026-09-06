"""
Integration tests for FastAPI REST API and OpenAI compatibility routes.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from api.app import app


@pytest.mark.asyncio
async def test_api_health_and_generate():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        resp_health = await client.get("/health")
        assert resp_health.status_code == 200
        assert resp_health.json()["status"] == "healthy"

        # 2. Generate Website
        resp_gen = await client.post(
            "/api/generate",
            json={
                "prompt": "Create an organic skincare product page",
                "system_mode": "specialized_multi_agent",
                "max_iterations": 1,
            }
        )
        assert resp_gen.status_code == 200
        gen_data = resp_gen.json()
        assert "run_id" in gen_data
        run_id = gen_data["run_id"]
        assert gen_data["status"] == "completed"

        # 3. Get Run Details
        resp_run = await client.get(f"/api/run/{run_id}")
        assert resp_run.status_code == 200

        # 4. Get Evaluation Report
        resp_eval = await client.get(f"/api/run/{run_id}/evaluation")
        assert resp_eval.status_code == 200

        # 5. Get Website Artifacts
        resp_site = await client.get(f"/api/run/{run_id}/website")
        assert resp_site.status_code == 200
        assert "<html" in resp_site.json()["html"]

        # 6. Preview Render
        resp_preview = await client.get(f"/api/preview/{run_id}/final")
        assert resp_preview.status_code == 200
        assert "Content-Security-Policy" in resp_preview.headers


@pytest.mark.asyncio
async def test_openai_compatibility_routes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Universal Generate
        resp = await client.post(
            "/v1/generate",
            json={"prompt": "Build a coffee shop website", "max_iterations": 1}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["object"] == "web_generation"
        assert "html" in data["website"]

        # Universal Evaluate
        resp_eval = await client.post(
            "/v1/evaluate",
            json={
                "html": "<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Coffee</h1></body></html>",
                "css": "h1 { color: brown; }",
                "prompt": "Evaluate coffee shop landing page"
            }
        )
        assert resp_eval.status_code == 200
        eval_data = resp_eval.json()
        assert eval_data["object"] == "web_evaluation"
        assert "metrics" in eval_data
