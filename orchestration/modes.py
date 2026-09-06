"""
System Modes and Ablation Configuration.
"""

from enum import Enum
from typing import List, Set


class SystemMode(str, Enum):
    GENERATOR_ONLY = "generator_only"
    GENERAL_CRITIC = "general_critic"
    SPECIALIZED_MULTI_AGENT = "specialized_multi_agent"


ALL_SPECIALIST_AGENTS: Set[str] = {
    "aesthetic",
    "accessibility",
    "usability",
    "ethics",
    "originality"
}


def get_active_agents(mode: SystemMode, ablated_agents: List[str] = None) -> List[str]:
    """Returns the list of active critic agents for the given mode and ablations."""
    ablated_set = {a.lower().strip() for a in (ablated_agents or [])}

    if mode == SystemMode.GENERATOR_ONLY:
        return []
    elif mode == SystemMode.GENERAL_CRITIC:
        return ["general_critic"]
    elif mode == SystemMode.SPECIALIZED_MULTI_AGENT:
        return [a for a in ["aesthetic", "accessibility", "usability", "ethics", "originality"] if a not in ablated_set]
    return []
