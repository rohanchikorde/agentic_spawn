"""
State management for AgentSpawn framework.

Defines the core state structures used throughout the agent orchestration system.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class AgentType(str, Enum):
    """Enumeration of available agent types."""
    DATA_ANALYST = "data_analyst"
    RESEARCHER = "researcher"
    CODE_GENERATOR = "code_generator"
    GENERAL = "general"


class ComplexityLevel(str, Enum):
    """Task complexity assessment levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


@dataclass
class TaskMetadata:
    """Metadata about the current task."""
    task_id: str
    created_at: datetime = field(default_factory=datetime.now)
    user_input: str = ""
    keywords: List[str] = field(default_factory=list)
    complexity: ComplexityLevel = ComplexityLevel.SIMPLE
    requires_multiple_agents: bool = False


@dataclass
class ToolUsage:
    """Information about tool usage by an agent."""
    tool_name: str
    agent_id: str
    used_at: datetime = field(default_factory=datetime.now)
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Any] = None
    success: bool = False
    error: Optional[str] = None
    execution_time: Optional[float] = None


@dataclass
class SpawnedAgent:
    """Information about a spawned agent."""
    agent_type: AgentType
    agent_id: str
    spawned_at: datetime = field(default_factory=datetime.now)
    status: str = "initialized"  # initialized, running, completed, failed
    result: Optional[str] = None
    error: Optional[str] = None


@dataclass
class OrchestratorState:
    """
    Main state object passed through the LangGraph workflow.
    
    This state tracks:
    - The original user task
    - Task complexity assessment
    - Spawned agents and their results
    - Tool usage by agents
    - Overall workflow progress
    """
    task_metadata: TaskMetadata
    spawned_agents: List[SpawnedAgent] = field(default_factory=list)
    tool_usage: List[ToolUsage] = field(default_factory=list)
    orchestrator_reasoning: str = ""
    spawned_agent_results: Dict[str, Any] = field(default_factory=dict)
    final_response: str = ""
    workflow_status: str = "initialized"  # initialized, assessing, spawning, executing, complete, failed
    error_messages: List[str] = field(default_factory=list)
    
    def add_agent(self, agent: SpawnedAgent) -> None:
        """Add a spawned agent to the state."""
        self.spawned_agents.append(agent)
    
    def update_agent_result(self, agent_id: str, result: str, status: str = "completed") -> None:
        """Update the result of a spawned agent."""
        for agent in self.spawned_agents:
            if agent.agent_id == agent_id:
                agent.result = result
                agent.status = status
                self.spawned_agent_results[agent_id] = result
                break
    
    def add_error(self, error: str) -> None:
        """Add an error message to the state."""
        self.error_messages.append(error)
        self.workflow_status = "failed"
    
    def add_tool_usage(self, tool_usage: ToolUsage) -> None:
        """Add tool usage to the state."""
        self.tool_usage.append(tool_usage)
    
    def get_agent_tool_usage(self, agent_id: str) -> List[ToolUsage]:
        """Get tool usage for a specific agent."""
        return [usage for usage in self.tool_usage if usage.agent_id == agent_id]
