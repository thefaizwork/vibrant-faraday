"""
Workspace Manager for Multi-Agent Runs.
Maintains versioned run directories, saves iterations, critiques, code files, and telemetry logs.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from orchestration.state import (
    IterationState,
    RunState,
    StructuredPrompt,
    WebsiteArtifacts,
)


class WorkspaceManager:
    def __init__(self, base_dir: Path = Path("./runs")):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_run_dir(self, run_id: str) -> Path:
        run_dir = self.base_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def get_iteration_dir(self, run_id: str, iteration: int) -> Path:
        iter_dir = self.get_run_dir(run_id) / f"iteration_{iteration:02d}"
        iter_dir.mkdir(parents=True, exist_ok=True)
        return iter_dir

    def save_structured_prompt(self, run_id: str, spec: StructuredPrompt) -> Path:
        run_dir = self.get_run_dir(run_id)
        spec_path = run_dir / "structured_prompt.json"
        with open(spec_path, "w", encoding="utf-8") as f:
            f.write(spec.model_dump_json(indent=2))
        return spec_path

    def save_iteration(
        self,
        run_id: str,
        iteration: int,
        spec: StructuredPrompt,
        website: WebsiteArtifacts,
        critiques: Dict[str, Any],
        aggregate: Optional[Any] = None,
        refinement: Optional[Any] = None,
        evaluation: Optional[Any] = None,
    ) -> Path:
        iter_dir = self.get_iteration_dir(run_id, iteration)

        # 1. Save prompt.json
        with open(iter_dir / "prompt.json", "w", encoding="utf-8") as f:
            f.write(spec.model_dump_json(indent=2))

        # 2. Save website files
        website_dir = iter_dir / "website"
        website_dir.mkdir(parents=True, exist_ok=True)
        with open(website_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(website.html)
        with open(website_dir / "styles.css", "w", encoding="utf-8") as f:
            f.write(website.css)
        with open(website_dir / "script.js", "w", encoding="utf-8") as f:
            f.write(website.javascript)
        if website.react_code:
            with open(website_dir / "page.tsx", "w", encoding="utf-8") as f:
                f.write(website.react_code)
        if website.backend_schema:
            with open(website_dir / "backend_schema.ts", "w", encoding="utf-8") as f:
                f.write(website.backend_schema)
        with open(website_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump({
                "component_structure": [c.model_dump() for c in website.component_structure],
                "metadata": website.metadata,
                "design_rationale": website.design_rationale,
                "framework": website.framework,
                "animation_stack": website.animation_stack
            }, f, indent=2)

        # 3. Save individual critiques
        critiques_dir = iter_dir / "critiques"
        critiques_dir.mkdir(parents=True, exist_ok=True)
        for agent_name, crit in critiques.items():
            crit_file = critiques_dir / f"{agent_name}.json"
            crit_data = crit.model_dump() if hasattr(crit, "model_dump") else crit
            with open(crit_file, "w", encoding="utf-8") as f:
                json.dump(crit_data, f, indent=2)

        # 4. Save aggregate.json
        if aggregate:
            agg_data = aggregate.model_dump() if hasattr(aggregate, "model_dump") else aggregate
            with open(iter_dir / "aggregate.json", "w", encoding="utf-8") as f:
                json.dump(agg_data, f, indent=2)

        # 5. Save refinement.json
        if refinement:
            ref_data = refinement.model_dump() if hasattr(refinement, "model_dump") else refinement
            with open(iter_dir / "refinement.json", "w", encoding="utf-8") as f:
                json.dump(ref_data, f, indent=2)

        # 6. Save evaluation.json
        if evaluation:
            eval_data = evaluation.model_dump() if hasattr(evaluation, "model_dump") else evaluation
            with open(iter_dir / "evaluation.json", "w", encoding="utf-8") as f:
                json.dump(eval_data, f, indent=2)

        return iter_dir

    def save_final_website(self, run_id: str, website: WebsiteArtifacts, state: RunState) -> Path:
        run_dir = self.get_run_dir(run_id)
        final_dir = run_dir / "final_website"
        final_dir.mkdir(parents=True, exist_ok=True)

        with open(final_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(website.html)
        with open(final_dir / "styles.css", "w", encoding="utf-8") as f:
            f.write(website.css)
        with open(final_dir / "script.js", "w", encoding="utf-8") as f:
            f.write(website.javascript)
        if website.react_code:
            with open(final_dir / "page.tsx", "w", encoding="utf-8") as f:
                f.write(website.react_code)
        if website.backend_schema:
            with open(final_dir / "backend_schema.ts", "w", encoding="utf-8") as f:
                f.write(website.backend_schema)

        # Save comprehensive final run summary
        with open(run_dir / "final_report.json", "w", encoding="utf-8") as f:
            f.write(state.model_dump_json(indent=2))

        return final_dir

    def log_telemetry(self, run_id: str, event_data: Dict[str, Any]) -> None:
        run_dir = self.get_run_dir(run_id)
        log_path = run_dir / "telemetry.jsonl"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_data) + "\n")

    def load_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        run_dir = self.get_run_dir(run_id)
        report_path = run_dir / "final_report.json"
        if report_path.exists():
            with open(report_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
