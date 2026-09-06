"""
Unit tests for all specialized agents.
"""

import pytest
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


@pytest.mark.asyncio
async def test_agent_lifecycle_and_critiques():
    # 1. Structurer
    structurer = PromptStructurerAgent()
    spec, tel_struct = await structurer.structure("Build an organic sustainable fashion website.")
    assert spec.project_goal != ""
    assert len(spec.target_users) > 0
    assert len(spec.acceptance_criteria) > 0
    assert tel_struct.success is True

    # 2. Generator
    generator = WebGeneratorAgent()
    website, tel_gen = await generator.generate(spec)
    assert "<html" in website.html
    assert len(website.css) > 0
    assert len(website.javascript) > 0
    assert len(website.component_structure) > 0

    # 3. Specialist Evaluation Agents
    aesthetic = AestheticAgent()
    aes_crit, _ = await aesthetic.evaluate(website, spec)
    assert 0.0 <= aes_crit.score <= 10.0

    accessibility = AccessibilityAgent()
    acc_crit, _ = await accessibility.evaluate(website, spec)
    assert 0.0 <= acc_crit.score <= 10.0

    usability = UsabilityAgent()
    usa_crit, _ = await usability.evaluate(website, spec)
    assert 0.0 <= usa_crit.score <= 10.0

    ethics = EthicsComplianceAgent()
    eth_crit, _ = await ethics.evaluate(website, spec)
    assert 0.0 <= eth_crit.score <= 10.0

    originality = OriginalityDiversityAgent()
    orig_crit, _ = await originality.evaluate(website, spec)
    assert 0.0 <= orig_crit.score <= 10.0

    general_critic = GeneralCriticAgent()
    gen_crit, _ = await general_critic.evaluate(website, spec)
    assert 0.0 <= gen_crit.score <= 10.0

    # 4. Feedback Aggregator
    critiques = {
        "aesthetic": aes_crit.model_dump(),
        "accessibility": acc_crit.model_dump(),
        "usability": usa_crit.model_dump(),
        "ethics": eth_crit.model_dump(),
        "originality": orig_crit.model_dump(),
    }
    aggregator = FeedbackAggregatorAgent()
    aggregate, _ = await aggregator.aggregate(critiques, spec)
    assert len(aggregate.priority_issues) > 0
    assert len(aggregate.preserve) > 0

    # 5. Design Refiner
    refiner = DesignRefinerAgent()
    refinement, _ = await refiner.refine(website, spec, aggregate)
    assert "<html" in refinement.revised_html
    assert len(refinement.change_summary) > 0
    assert len(refinement.issue_mappings) > 0
