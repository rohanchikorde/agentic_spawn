"""
AgentSpawn framework initialization.

Main entry point for the AgentSpawn framework.
"""

from orchestrator import Orchestrator
from agent_registry import get_registry, AgentRegistry
from state import OrchestratorState, TaskMetadata, SpawnedAgent

__version__ = "0.1.0"
__all__ = [
    "Orchestrator",
    "get_registry",
    "AgentRegistry",
    "OrchestratorState",
    "TaskMetadata",
    "SpawnedAgent"
]
