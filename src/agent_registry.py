"""
Agent registry system for AgentSpawn framework.

Manages agent templates, configurations, and factory methods for creating agents.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from state import AgentType


@dataclass
class AgentConfig:
    """Configuration for an agent type."""
    agent_type: AgentType
    name: str
    description: str
    system_prompt: str
    capabilities: List[str]
    max_retries: int = 3
    timeout: int = 30


class AgentRegistry:
    """
    Registry for managing agent templates and configurations.
    
    This system allows for:
    - Registering new agent types
    - Retrieving agent configurations
    - Factory methods for agent creation
    - Agent capability discovery
    """
    
    def __init__(self):
        """Initialize the registry with default agents."""
        self._agents: Dict[str, AgentConfig] = {}
        self._initialize_default_agents()
    
    def _initialize_default_agents(self) -> None:
        """Initialize the framework with three default agent types."""
        
        # Data Analyst Agent
        data_analyst_config = AgentConfig(
            agent_type=AgentType.DATA_ANALYST,
            name="Data Analyst",
            description="Specializes in data analysis, statistics, and insights extraction",
            system_prompt="""You are an expert data analyst with deep knowledge of statistics, data visualization,
and business intelligence. You excel at:
- Identifying patterns and trends in data
- Performing statistical analysis
- Creating actionable insights
- Recommending data-driven decisions

Always provide quantitative backing for your claims and consider multiple perspectives.""",
            capabilities=[
                "statistical_analysis",
                "data_aggregation",
                "trend_identification",
                "metric_calculation",
                "anomaly_detection",
                "forecasting"
            ]
        )
        self.register_agent(data_analyst_config)
        
        # Researcher Agent
        researcher_config = AgentConfig(
            agent_type=AgentType.RESEARCHER,
            name="Research Specialist",
            description="Conducts comprehensive research, gathers information, and provides context",
            system_prompt="""You are a thorough research specialist with expertise in:
- Information gathering and synthesis
- Literature review and source evaluation
- Contextual analysis
- Pattern recognition across domains

Always cite sources, acknowledge limitations, and provide comprehensive background information.
Consider multiple viewpoints and present balanced analysis.""",
            capabilities=[
                "information_gathering",
                "source_evaluation",
                "literature_review",
                "context_analysis",
                "comparative_analysis",
                "hypothesis_formation"
            ]
        )
        self.register_agent(researcher_config)
        
        # Code Generator Agent
        code_generator_config = AgentConfig(
            agent_type=AgentType.CODE_GENERATOR,
            name="Code Generator",
            description="Generates code, provides implementation guidance, and engineering solutions",
            system_prompt="""You are an expert software engineer with proficiency in multiple languages.
You excel at:
- Writing clean, maintainable code
- Implementing algorithms efficiently
- Following design patterns and best practices
- Providing architectural guidance

Always prioritize code quality, readability, and performance. Include comments and docstrings.
Consider edge cases and error handling.""",
            capabilities=[
                "code_generation",
                "algorithm_implementation",
                "architecture_design",
                "debugging",
                "optimization",
                "documentation_generation"
            ]
        )
        self.register_agent(code_generator_config)
    
    def register_agent(self, config: AgentConfig) -> None:
        """
        Register a new agent type or update existing configuration.
        
        Args:
            config: AgentConfig instance
        """
        self._agents[config.agent_type.value] = config
    
    def get_agent_config(self, agent_type: str) -> AgentConfig:
        """
        Retrieve configuration for an agent type.
        
        Args:
            agent_type: The agent type identifier
            
        Returns:
            AgentConfig for the requested agent
            
        Raises:
            ValueError: If agent type is not registered
        """
        if agent_type not in self._agents:
            raise ValueError(f"Agent type '{agent_type}' not found in registry")
        return self._agents[agent_type]
    
    def list_agents(self) -> Dict[str, AgentConfig]:
        """
        Get all registered agents.
        
        Returns:
            Dictionary of all registered agent configurations
        """
        return self._agents.copy()
    
    def get_agent_capabilities(self, agent_type: str) -> List[str]:
        """
        Get capabilities for a specific agent type.
        
        Args:
            agent_type: The agent type identifier
            
        Returns:
            List of agent capabilities
        """
        config = self.get_agent_config(agent_type)
        return config.capabilities
    
    def has_agent(self, agent_type: str) -> bool:
        """
        Check if an agent type is registered.
        
        Args:
            agent_type: The agent type identifier
            
        Returns:
            True if agent is registered, False otherwise
        """
        return agent_type in self._agents
    
    def get_agent_by_capability(self, capability: str) -> List[str]:
        """
        Find agents that have a specific capability.
        
        Args:
            capability: The capability to search for
            
        Returns:
            List of agent type identifiers with this capability
        """
        matching_agents = []
        for agent_type, config in self._agents.items():
            if capability in config.capabilities:
                matching_agents.append(agent_type)
        return matching_agents


# Global registry instance
_global_registry: AgentRegistry = None


def get_registry() -> AgentRegistry:
    """
    Get the global agent registry instance (singleton pattern).
    
    Returns:
        The global AgentRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = AgentRegistry()
    return _global_registry


def reset_registry() -> None:
    """Reset the global registry (useful for testing)."""
    global _global_registry
    _global_registry = None
