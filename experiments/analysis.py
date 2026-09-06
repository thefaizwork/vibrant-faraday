"""
Experiment Analysis & Comparative Reporting.
Compares Generator-Only, General Critic, and Specialized Multi-Agent experimental outcomes.
"""

import json
from pathlib import Path
from typing import Any, Dict, List


class ExperimentAnalyzer:
    @classmethod
    def generate_comparison_table(cls, experiment_json_files: List[Path]) -> str:
        """
        Reads multiple experiment JSON files and generates a Markdown comparison table.
        """
        summaries = []
        for p in experiment_json_files:
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "summary" in data:
                        summaries.append(data["summary"])

        if not summaries:
            return "No experiment summaries available."

        md = "# Multi-Agent Web Design Generation: Comparative Research Results\n\n"
        md += "| System Mode | Tasks | Composite Score | Aesthetic | Accessibility | Usability | Ethics | Originality | Mean Iters | Latency (s) | Cost ($) |\n"
        md += "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n"

        for s in summaries:
            mode_lbl = s.get("system_mode", "unknown")
            ablated = s.get("ablated_agents", [])
            if ablated:
                mode_lbl += f" (no {','.join(ablated)})"

            comp = s.get("mean_composite_score", 0.0)
            aes = s.get("mean_aesthetic_score", "-")
            acc = s.get("mean_accessibility_score", "-")
            usa = s.get("mean_usability_score", "-")
            eth = s.get("mean_ethics_score", "-")
            orig = s.get("mean_originality_score", "-")
            iters = s.get("mean_iterations", 1.0)
            lat = round(s.get("mean_latency_ms", 0.0) / 1000.0, 2)
            cost = s.get("total_cost_usd", 0.0)

            md += f"| **{mode_lbl}** | {s.get('total_tasks', 0)} | **{comp}** | {aes} | {acc} | {usa} | {eth} | {orig} | {iters} | {lat}s | ${cost:.4f} |\n"

        md += "\n> [!NOTE]\n"
        md += "> All experiments were evaluated across identical benchmark prompts and objective evaluation criteria.\n"

        return md
