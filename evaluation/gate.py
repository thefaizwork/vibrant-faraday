"""
Evaluation Gate & Termination Logic.
Determines whether a generated candidate passes quality thresholds or requires another refinement loop.
"""

from typing import Tuple
from config.settings import settings
from orchestration.state import EvaluationMetrics, FeedbackAggregate


class EvaluationGate:
    @classmethod
    def evaluate(
        cls,
        metrics: EvaluationMetrics,
        aggregate: FeedbackAggregate,
        current_iteration: int,
        max_iterations: int = settings.max_iterations,
        quality_threshold: float = settings.quality_threshold,
        cost_usd: float = 0.0,
        cost_limit_usd: float = settings.cost_limit_usd,
        elapsed_seconds: float = 0.0,
        time_limit_seconds: int = settings.time_limit_seconds,
    ) -> Tuple[bool, str]:
        """
        Evaluates termination conditions:
        Returns (passed, reason_string).
        """
        # 1. Check Budget and Time limits
        if cost_usd >= cost_limit_usd:
            return True, f"Terminated: Cost limit reached (${cost_usd:.3f} >= ${cost_limit_usd:.2f})"

        if elapsed_seconds >= time_limit_seconds:
            return True, f"Terminated: Time limit reached ({elapsed_seconds:.1f}s >= {time_limit_seconds}s)"

        # 2. Check Blocking Issues
        if aggregate.blocking_issues:
            if current_iteration >= max_iterations:
                return True, f"Terminated at max iterations ({current_iteration}) with unresolved blocking issues."
            return False, f"Refinement required: {len(aggregate.blocking_issues)} blocking issue(s) detected."

        # 3. Check Quality Threshold
        if metrics.composite_score >= quality_threshold:
            return True, f"Passed Gate: Composite score {metrics.composite_score:.2f} satisfies quality threshold {quality_threshold:.2f}."

        # 4. Check Max Iterations
        if current_iteration >= max_iterations:
            return True, f"Terminated: Reached max iterations ({current_iteration}/{max_iterations}). Final score: {metrics.composite_score:.2f}."

        return False, f"Refinement required: Composite score {metrics.composite_score:.2f} < threshold {quality_threshold:.2f}."
