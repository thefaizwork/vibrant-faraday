"""
Evaluation metrics calculation and scoring engine.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from orchestration.state import EvaluationMetrics
from providers.base import TokenUsage


def _get_val(obj: Any, key: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if hasattr(obj, key):
        return getattr(obj, key)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


class MetricsEngine:
    @classmethod
    def compute_composite_metrics(
        cls,
        agent_critiques: Dict[str, Any],
        static_analysis: Optional[Dict[str, Any]] = None,
        latency_ms: float = 0.0,
        token_usage: Optional[TokenUsage] = None,
    ) -> EvaluationMetrics:
        """
        Combines specialist agent critiques and static checks into composite metrics.
        """
        aesthetic_score = None
        accessibility_score = None
        usability_score = None
        ethics_score = None
        originality_score = None
        general_score = None

        # Extract scores from critiques
        if "aesthetic" in agent_critiques:
            aesthetic_score = float(_get_val(agent_critiques["aesthetic"], "score", 0.0))

        if "accessibility" in agent_critiques:
            llm_acc = float(_get_val(agent_critiques["accessibility"], "score", 0.0))
            if static_analysis and "wcag_score" in static_analysis:
                # Blend LLM review (60%) and deterministic static WCAG check (40%)
                static_acc = static_analysis["wcag_score"]
                accessibility_score = round(0.6 * llm_acc + 0.4 * static_acc, 2)
            else:
                accessibility_score = llm_acc

        if "usability" in agent_critiques:
            usability_score = float(_get_val(agent_critiques["usability"], "score", 0.0))

        if "ethics" in agent_critiques:
            llm_eth = float(_get_val(agent_critiques["ethics"], "score", 0.0))
            if static_analysis and "ethics_static_score" in static_analysis:
                static_eth = static_analysis["ethics_static_score"]
                ethics_score = round(0.7 * llm_eth + 0.3 * static_eth, 2)
            else:
                ethics_score = llm_eth

        if "originality" in agent_critiques:
            originality_score = float(_get_val(agent_critiques["originality"], "score", 0.0))

        if "general_critic" in agent_critiques:
            general_score = float(_get_val(agent_critiques["general_critic"], "score", 0.0))

        # Determine composite score based on available dimensional scores
        scores: List[float] = []
        if aesthetic_score is not None:
            scores.append(aesthetic_score)
        if accessibility_score is not None:
            scores.append(accessibility_score)
        if usability_score is not None:
            scores.append(usability_score)
        if ethics_score is not None:
            scores.append(ethics_score)
        if originality_score is not None:
            scores.append(originality_score)
        if general_score is not None and not scores:
            scores.append(general_score)

        if not scores and static_analysis:
            if "wcag_score" in static_analysis:
                accessibility_score = static_analysis["wcag_score"]
                scores.append(accessibility_score)
            if "ethics_static_score" in static_analysis:
                ethics_score = static_analysis["ethics_static_score"]
                scores.append(ethics_score)

        composite_score = round(sum(scores) / len(scores), 2) if scores else 0.0

        dark_pattern_count = 0
        if "ethics" in agent_critiques:
            dark_patterns = _get_val(agent_critiques["ethics"], "dark_patterns_detected", [])
            dark_pattern_count += len(dark_patterns) if isinstance(dark_patterns, list) else 0
        if static_analysis:
            dark_pattern_count = max(dark_pattern_count, static_analysis.get("dark_pattern_count", 0))

        wcag_pass_rate = 100.0
        if static_analysis and "critical_issues" in static_analysis:
            crit_count = len(static_analysis["critical_issues"])
            wcag_pass_rate = max(0.0, round(100.0 - (crit_count * 25.0), 1))

        return EvaluationMetrics(
            aesthetic_score=aesthetic_score,
            accessibility_score=accessibility_score,
            usability_score=usability_score,
            ethics_score=ethics_score,
            originality_score=originality_score,
            general_score=general_score,
            composite_score=composite_score,
            wcag_pass_rate=wcag_pass_rate,
            dark_pattern_count=dark_pattern_count,
            latency_ms=latency_ms,
            token_usage=token_usage or TokenUsage(),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
