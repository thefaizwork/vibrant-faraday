"""
Central Multi-Agent Orchestration Engine.
Coordinates Prompt Structuring, Web Generation, Concurrent Criticisms, Aggregation, Refinement, and Gate Evaluation.
"""

import asyncio
from datetime import datetime, timezone
import time
import uuid
from typing import Any, Dict, List, Optional
from config.settings import settings
from agents.prompt_structurer.structurer import PromptStructurerAgent
from agents.generator.generator import WebGeneratorAgent
from agents.aesthetic.aesthetic_agent import AestheticAgent
from agents.accessibility.accessibility_agent import AccessibilityAgent
from agents.usability.usability_agent import UsabilityAgent
from agents.ethics.ethics_agent import EthicsComplianceAgent
from agents.originality.originality_agent import OriginalityDiversityAgent
from agents.general_critic.general_critic_agent import GeneralCriticAgent
from agents.aggregator.aggregator import FeedbackAggregatorAgent
from agents.refiner.refiner import DesignRefinerAgent
from evaluation.gate import EvaluationGate
from evaluation.metrics import MetricsEngine
from evaluation.static_analyzer import StaticAnalyzer
from orchestration.modes import SystemMode, get_active_agents
from orchestration.state import (
    DesignRefinement,
    EvaluationMetrics,
    FeedbackAggregate,
    IterationState,
    RunState,
    StructuredPrompt,
    WebsiteArtifacts,
)
from providers.base import TokenUsage
from storage.database import Database
from storage.workspace import WorkspaceManager


class Orchestrator:
    def __init__(
        self,
        workspace_manager: Optional[WorkspaceManager] = None,
        db: Optional[Database] = None,
    ):
        self.workspace = workspace_manager or WorkspaceManager(settings.workspace_dir)
        self.db = db or Database(settings.database_url.replace("sqlite:///", ""))

        # Initialize Agents
        self.structurer = PromptStructurerAgent()
        self.generator = WebGeneratorAgent()
        self.aesthetic_agent = AestheticAgent()
        self.accessibility_agent = AccessibilityAgent()
        self.usability_agent = UsabilityAgent()
        self.ethics_agent = EthicsComplianceAgent()
        self.originality_agent = OriginalityDiversityAgent()
        self.general_critic = GeneralCriticAgent()
        self.aggregator = FeedbackAggregatorAgent()
        self.refiner = DesignRefinerAgent()

    async def run_pipeline(
        self,
        prompt: str,
        system_mode: Optional[SystemMode] = None,
        ablated_agents: Optional[List[str]] = None,
        max_iterations: Optional[int] = None,
        quality_threshold: Optional[float] = None,
        run_id: Optional[str] = None,
        framework: str = "vanilla_gsap_lenis",
        animation_stack: str = "gsap_lenis",
    ) -> RunState:
        """
        Executes the closed-loop multi-agent generation & refinement pipeline.
        """
        mode = system_mode or settings.system_mode
        active_agents = get_active_agents(mode, ablated_agents or [])
        max_iters = max_iterations or settings.max_iterations
        threshold = quality_threshold or settings.quality_threshold
        run_id = run_id or f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

        start_time = time.perf_counter()
        total_tokens = TokenUsage()

        state = RunState(
            run_id=run_id,
            original_prompt=prompt,
            system_mode=mode.value if hasattr(mode, "value") else str(mode),
            ablated_agents=ablated_agents or [],
            current_iteration=0,
            status="in_progress",
        )

        self._log_event(run_id, "run_started", {
            "prompt": prompt,
            "mode": state.system_mode,
            "active_agents": active_agents,
            "framework": framework,
            "animation_stack": animation_stack
        })

        try:
            # 1. Prompt Structuring Phase
            self._log_event(run_id, "structuring_prompt_started", {})
            spec, struct_tel = await self.structurer.structure(prompt)
            state.structured_prompt = spec
            self._accumulate_tokens(total_tokens, struct_tel.token_usage)
            self.workspace.save_structured_prompt(run_id, spec)
            self._log_event(run_id, "structuring_prompt_completed", {"spec": spec.model_dump()})

            # 2. Initial Website Generation Phase
            self._log_event(run_id, "initial_generation_started", {})
            website, gen_tel = await self.generator.generate(spec, framework=framework, animation_stack=animation_stack)
            self._accumulate_tokens(total_tokens, gen_tel.token_usage)
            self._log_event(run_id, "initial_generation_completed", {"title": website.metadata.get("title")})

            current_site = website
            iteration = 1

            # Generator-Only Baseline Mode
            if mode == SystemMode.GENERATOR_ONLY:
                # Perform one static & metrics assessment for reporting
                static_res = StaticAnalyzer.analyze(current_site.html, current_site.css, current_site.javascript)
                metrics = MetricsEngine.compute_composite_metrics(
                    agent_critiques={},
                    static_analysis=static_res,
                    latency_ms=(time.perf_counter() - start_time) * 1000,
                    token_usage=total_tokens,
                )
                metrics.passed_gate = True
                metrics.gate_reason = "Generator-only single pass baseline completed."

                iter_state = IterationState(
                    iteration_number=1,
                    website=current_site,
                    critiques={},
                    evaluation=metrics,
                )
                state.history.append(iter_state)
                state.current_iteration = 1
                state.evaluation = metrics

                self.workspace.save_iteration(
                    run_id=run_id,
                    iteration=1,
                    spec=spec,
                    website=current_site,
                    critiques={},
                    evaluation=metrics,
                )
                self.workspace.save_final_website(run_id, current_site, state)

                state.status = "completed"
                state.end_time = datetime.now(timezone.utc).isoformat()
                state.total_latency_ms = (time.perf_counter() - start_time) * 1000
                state.total_token_usage = total_tokens
                self.db.save_run(state)
                self._log_event(run_id, "run_completed", {"composite_score": metrics.composite_score})
                return state

            # Iterative Multi-Agent Refinement Loop
            while iteration <= max_iters:
                state.current_iteration = iteration
                self._log_event(run_id, f"iteration_{iteration}_started", {"iteration": iteration})

                # 3. Concurrent Critiques from Active Agents
                critiques, critique_tokens = await self._run_critiques(current_site, spec, active_agents)
                self._accumulate_tokens(total_tokens, critique_tokens)
                state.agent_results = {k: v.model_dump() if hasattr(v, "model_dump") else v for k, v in critiques.items()}

                # Static Analysis
                static_res = StaticAnalyzer.analyze(current_site.html, current_site.css, current_site.javascript)

                # Compute Evaluation Metrics
                metrics = MetricsEngine.compute_composite_metrics(
                    agent_critiques=state.agent_results,
                    static_analysis=static_res,
                    latency_ms=(time.perf_counter() - start_time) * 1000,
                    token_usage=total_tokens,
                )

                # 4. Aggregation Phase
                self._log_event(run_id, "feedback_aggregation_started", {"critiques_count": len(critiques)})
                aggregate, agg_tel = await self.aggregator.aggregate(state.agent_results, spec)
                self._accumulate_tokens(total_tokens, agg_tel.token_usage)
                state.aggregate_feedback = aggregate

                # 5. Evaluation Gate Check
                elapsed_sec = time.perf_counter() - start_time
                passed_gate, gate_reason = EvaluationGate.evaluate(
                    metrics=metrics,
                    aggregate=aggregate,
                    current_iteration=iteration,
                    max_iterations=max_iters,
                    quality_threshold=threshold,
                    cost_usd=total_tokens.estimated_cost_usd,
                    elapsed_seconds=elapsed_sec,
                )
                metrics.passed_gate = passed_gate
                metrics.gate_reason = gate_reason
                state.evaluation = metrics

                refinement: Optional[DesignRefinement] = None

                # 6. Refinement Step (if gate not satisfied and iterations remain)
                if not passed_gate and iteration < max_iters:
                    self._log_event(run_id, "design_refinement_started", {"strategy": aggregate.refinement_strategy})
                    refinement, ref_tel = await self.refiner.refine(current_site, spec, aggregate)
                    self._accumulate_tokens(total_tokens, ref_tel.token_usage)

                    # Update current website candidate with refined code
                    current_site = WebsiteArtifacts(
                        html=refinement.revised_html,
                        css=refinement.revised_css,
                        javascript=refinement.revised_js,
                        framework=current_site.framework,
                        animation_stack=current_site.animation_stack,
                        react_code=current_site.react_code,
                        backend_schema=current_site.backend_schema,
                        files=current_site.files,
                        component_structure=current_site.component_structure,
                        metadata=current_site.metadata,
                        design_rationale=current_site.design_rationale,
                    )
                    self._log_event(run_id, "design_refinement_completed", {"change_summary": refinement.change_summary})

                # Record Iteration State
                iter_state = IterationState(
                    iteration_number=iteration,
                    website=current_site,
                    critiques=state.agent_results,
                    aggregate=aggregate,
                    refinement=refinement,
                    evaluation=metrics,
                )
                state.history.append(iter_state)

                # Save workspace files
                self.workspace.save_iteration(
                    run_id=run_id,
                    iteration=iteration,
                    spec=spec,
                    website=current_site,
                    critiques=critiques,
                    aggregate=aggregate,
                    refinement=refinement,
                    evaluation=metrics,
                )

                if passed_gate or iteration >= max_iters:
                    break

                iteration += 1

            # Finalize Run
            self.workspace.save_final_website(run_id, current_site, state)
            state.status = "completed"
            state.end_time = datetime.now(timezone.utc).isoformat()
            state.total_latency_ms = (time.perf_counter() - start_time) * 1000
            state.total_token_usage = total_tokens

            self.db.save_run(state)
            self._log_event(run_id, "run_completed", {
                "composite_score": state.evaluation.composite_score if state.evaluation else 0.0,
                "iterations_completed": state.current_iteration,
                "passed_gate": state.evaluation.passed_gate if state.evaluation else False
            })

            return state

        except Exception as e:
            state.status = "failed"
            state.error_message = str(e)
            state.end_time = datetime.now(timezone.utc).isoformat()
            state.total_latency_ms = (time.perf_counter() - start_time) * 1000
            self.db.save_run(state)
            self._log_event(run_id, "run_failed", {"error": str(e)})
            raise

    async def _run_critiques(
        self,
        website: WebsiteArtifacts,
        spec: StructuredPrompt,
        active_agents: List[str]
    ) -> tuple[Dict[str, Any], TokenUsage]:
        """Runs active critic agents concurrently."""
        tasks = []
        task_names = []

        for agent_name in active_agents:
            if agent_name == "aesthetic":
                tasks.append(self.aesthetic_agent.evaluate(website, spec))
                task_names.append("aesthetic")
            elif agent_name == "accessibility":
                tasks.append(self.accessibility_agent.evaluate(website, spec))
                task_names.append("accessibility")
            elif agent_name == "usability":
                tasks.append(self.usability_agent.evaluate(website, spec))
                task_names.append("usability")
            elif agent_name == "ethics":
                tasks.append(self.ethics_agent.evaluate(website, spec))
                task_names.append("ethics")
            elif agent_name == "originality":
                tasks.append(self.originality_agent.evaluate(website, spec))
                task_names.append("originality")
            elif agent_name == "general_critic":
                tasks.append(self.general_critic.evaluate(website, spec))
                task_names.append("general_critic")

        results = await asyncio.gather(*tasks, return_exceptions=True)

        critiques: Dict[str, Any] = {}
        total_tokens = TokenUsage()

        for name, res in zip(task_names, results):
            if isinstance(res, Exception):
                # Isolate failure: do not crash whole run if one specialist fails
                critiques[name] = {"score": 7.0, "issues": [f"Agent evaluation error: {str(res)}"], "recommendations": []}
            else:
                critique_obj, telemetry = res
                critiques[name] = critique_obj
                self._accumulate_tokens(total_tokens, telemetry.token_usage)

        return critiques, total_tokens

    def _accumulate_tokens(self, target: TokenUsage, delta: TokenUsage):
        target.prompt_tokens += delta.prompt_tokens
        target.completion_tokens += delta.completion_tokens
        target.total_tokens += delta.total_tokens
        target.estimated_cost_usd += delta.estimated_cost_usd

    def _log_event(self, run_id: str, event_type: str, payload: Dict[str, Any]):
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": run_id,
            "event": event_type,
            "data": payload
        }
        self.workspace.log_telemetry(run_id, event)
