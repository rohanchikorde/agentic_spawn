"""
Orchestrator module for AgentSpawn framework.

Implements the main orchestrator agent that assesses task complexity and spawns
specialized agents only when needed. Uses LangGraph for workflow management.
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import dotenv

from .state import (
    OrchestratorState, TaskMetadata, SpawnedAgent, AgentType,
    ComplexityLevel
)
from .utils import (
    assess_task_complexity, detect_required_agents, extract_keywords,
    generate_agent_id, create_agent_prompt
)
from .agent_registry import get_registry


# Load environment variables
dotenv.load_dotenv()


class Orchestrator:
    """
    Main orchestrator agent that analyzes task complexity and spawns sub-agents.
    
    This class implements:
    - Task complexity assessment using keyword patterns
    - Agent spawning decisions based on complexity
    - Workflow orchestration using LangGraph
    - Result aggregation from spawned agents
    """
    
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.7):
        """
        Initialize the orchestrator.
        
        Args:
            model_name: LLM model to use (default: gpt-4)
            temperature: Temperature for LLM responses
        """
        self.model_name = model_name
        self.temperature = temperature
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.registry = get_registry()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow for orchestration.
        
        Returns:
            Configured StateGraph
        """
        workflow = StateGraph(OrchestratorState)
        
        # Add workflow nodes
        workflow.add_node("assess_complexity", self.assess_complexity_node)
        workflow.add_node("decide_agents", self.decide_agents_node)
        workflow.add_node("spawn_agents", self.spawn_agents_node)
        workflow.add_node("aggregate_results", self.aggregate_results_node)
        
        # Add edges
        workflow.set_entry_point("assess_complexity")
        workflow.add_edge("assess_complexity", "decide_agents")
        workflow.add_edge("decide_agents", "spawn_agents")
        workflow.add_edge("spawn_agents", "aggregate_results")
        workflow.add_edge("aggregate_results", END)
        
        return workflow.compile()
    
    def assess_complexity_node(self, state: OrchestratorState) -> OrchestratorState:
        """
        Assess the complexity of the task.
        
        Uses keyword detection and pattern matching to determine task complexity.
        
        Args:
            state: Current orchestrator state
            
        Returns:
            Updated state with complexity assessment
        """
        task = state.task_metadata.user_input
        
        # Extract keywords
        keywords = extract_keywords(task)
        state.task_metadata.keywords = keywords
        
        # Assess complexity
        complexity = assess_task_complexity(task, keywords)
        state.task_metadata.complexity = complexity
        
        # Generate reasoning
        reasoning = f"Assessed task complexity as {complexity.value}. "
        reasoning += f"Keywords identified: {', '.join(keywords[:5])}. "
        
        if complexity == ComplexityLevel.SIMPLE:
            reasoning += "Task is straightforward and can be handled by general reasoning."
        elif complexity == ComplexityLevel.MODERATE:
            reasoning += "Task requires specialized analysis. Specialized agents may be beneficial."
        else:
            reasoning += "Task is complex. Multiple specialized agents will be spawned."
        
        state.orchestrator_reasoning = reasoning
        state.workflow_status = "assessing"
        
        return state
    
    def decide_agents_node(self, state: OrchestratorState) -> OrchestratorState:
        """
        Decide which agents to spawn based on complexity and requirements.
        
        Uses keyword detection to identify required agent types.
        
        Args:
            state: Current orchestrator state
            
        Returns:
            Updated state with agent spawning decision
        """
        task = state.task_metadata.user_input
        keywords = state.task_metadata.keywords
        complexity = state.task_metadata.complexity
        
        # Detect required agents based on keywords
        required_agents = detect_required_agents(task, keywords)
        
        # Decision logic: spawn agents based on complexity and detected needs
        agents_to_spawn = []
        
        if complexity == ComplexityLevel.SIMPLE:
            # Simple tasks don't require specialized agents
            agents_to_spawn = []
        elif complexity == ComplexityLevel.MODERATE:
            # Moderate complexity: spawn detected agents
            agents_to_spawn = required_agents
        else:  # COMPLEX
            # Complex tasks: always spawn specialized agents, prioritize detected ones
            agents_to_spawn = required_agents
            # If no specific agents detected, spawn data_analyst and researcher
            if not agents_to_spawn:
                agents_to_spawn = ["data_analyst", "researcher"]
        
        state.task_metadata.requires_multiple_agents = len(agents_to_spawn) > 1
        
        # Store decision in reasoning
        if agents_to_spawn:
            state.orchestrator_reasoning += (
                f"\nSpawning {len(agents_to_spawn)} agents: {', '.join(agents_to_spawn)}"
            )
        else:
            state.orchestrator_reasoning += "\nNo specialized agents needed. Using direct reasoning."
        
        state.workflow_status = "deciding_agents"
        
        return state
    
    def spawn_agents_node(self, state: OrchestratorState) -> OrchestratorState:
        """
        Spawn the required agents and execute them.
        
        Args:
            state: Current orchestrator state
            
        Returns:
            Updated state with spawned agents and their results
        """
        task = state.task_metadata.user_input
        required_agents = detect_required_agents(task, state.task_metadata.keywords)
        
        state.workflow_status = "spawning"
        
        if not required_agents:
            # No agents to spawn, handle with direct LLM reasoning
            state.workflow_status = "executing"
            response = self._direct_reasoning(task)
            state.final_response = response
            return state
        
        # Spawn and execute each required agent
        for agent_type in required_agents:
            agent_id = generate_agent_id(agent_type)
            
            try:
                agent = SpawnedAgent(agent_type=AgentType(agent_type), agent_id=agent_id)
                state.add_agent(agent)
                
                # Execute the agent
                agent_response = self._execute_agent(agent_type, task, state)
                
                state.update_agent_result(agent_id, agent_response, "completed")
                
            except Exception as e:
                error_msg = f"Error executing agent {agent_type}: {str(e)}"
                state.add_error(error_msg)
                state.update_agent_result(agent_id, "", "failed")
        
        state.workflow_status = "executed"
        return state
    
    def aggregate_results_node(self, state: OrchestratorState) -> OrchestratorState:
        """
        Aggregate results from spawned agents into final response.
        
        Args:
            state: Current orchestrator state
            
        Returns:
            Updated state with aggregated final response
        """
        state.workflow_status = "aggregating"
        
        # If no agents were spawned and direct reasoning was used
        if not state.spawned_agents:
            state.workflow_status = "complete"
            return state
        
        # Aggregate results from all agents
        if state.spawned_agent_results:
            aggregated_response = self._aggregate_agent_results(
                state.task_metadata.user_input,
                state.spawned_agent_results
            )
            state.final_response = aggregated_response
        else:
            state.final_response = state.orchestrator_reasoning
        
        state.workflow_status = "complete"
        return state
    
    def _execute_agent(self, agent_type: str, task: str, state: OrchestratorState) -> str:
        """
        Execute a specific agent with the given task.

        Args:
            agent_type: Type of agent to execute
            task: Task for the agent to perform
            state: Current orchestrator state for tool tracking

        Returns:
            Agent's response/result
        """
        try:
            config = self.registry.get_agent_config(agent_type)
        except ValueError:
            return f"Agent type {agent_type} not found"

        # Get the agent instance from registry
        agent_instance = self.registry.get_agent_instance(agent_type)
        if not agent_instance:
            # Fallback to LLM-only execution
            prompt = create_agent_prompt(agent_type, task)
            messages = [
                SystemMessage(content=config.system_prompt),
                HumanMessage(content=prompt)
            ]
            response = self.llm.invoke(messages)
            return response.content

        # Execute agent with tool support
        try:
            if hasattr(agent_instance, 'analyze'):
                # Data analyst agent
                result = agent_instance.analyze(task, tool_usage=state.tool_usage)
                # Add tool usage to state
                state.tool_usage.extend(result.get('tool_usage', []))
                return result.get('analysis', 'No analysis provided')
            else:
                # Other agents - fallback to LLM
                prompt = create_agent_prompt(agent_type, task)
                messages = [
                    SystemMessage(content=config.system_prompt),
                    HumanMessage(content=prompt)
                ]
                response = self.llm.invoke(messages)
                return response.content

        except Exception as e:
            return f"Agent execution failed: {str(e)}"
    
    def _direct_reasoning(self, task: str) -> str:
        """
        Perform direct reasoning without spawning agents.
        
        Args:
            task: The task to reason about
            
        Returns:
            LLM response
        """
        system_prompt = """You are a helpful AI assistant. Provide clear, concise, and accurate answers.
Focus on being direct and practical in your responses."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=task)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def _aggregate_agent_results(self, task: str, results: Dict[str, str]) -> str:
        """
        Aggregate results from multiple agents into a cohesive response.
        
        Args:
            task: Original task
            results: Dictionary of agent_id -> result
            
        Returns:
            Aggregated final response
        """
        results_summary = "\n\n".join([
            f"**{agent_id}:**\n{result}"
            for agent_id, result in results.items()
        ])
        
        aggregation_prompt = f"""Please synthesize the following specialized analyses into a comprehensive response to the original task:

Original Task: {task}

Specialist Reports:
{results_summary}

Provide a unified, cohesive response that leverages insights from all specialists."""
        
        messages = [
            SystemMessage(content="You are an expert synthesizer who combines insights from multiple specialists into clear, actionable recommendations."),
            HumanMessage(content=aggregation_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def process_task(self, task: str) -> Dict[str, Any]:
        """
        Process a complete task through the orchestration workflow.
        
        Args:
            task: User's task description
            
        Returns:
            Dictionary containing:
            - final_response: The final aggregated response
            - task_metadata: Information about the task
            - spawned_agents: List of spawned agents
            - orchestrator_reasoning: Orchestrator's reasoning process
        """
        # Create initial state
        task_metadata = TaskMetadata(
            task_id=generate_agent_id("task"),
            user_input=task
        )
        
        initial_state = OrchestratorState(task_metadata=task_metadata)
        
        # Execute workflow
        final_state = self.workflow.invoke(initial_state)
        
        # Return results
        return {
            "final_response": final_state.final_response,
            "task_metadata": {
                "task_id": final_state.task_metadata.task_id,
                "complexity": final_state.task_metadata.complexity.value,
                "keywords": final_state.task_metadata.keywords,
                "requires_multiple_agents": final_state.task_metadata.requires_multiple_agents
            },
            "spawned_agents": [
                {
                    "agent_type": agent.agent_type.value,
                    "agent_id": agent.agent_id,
                    "status": agent.status,
                    "result": agent.result
                }
                for agent in final_state.spawned_agents
            ],
            "orchestrator_reasoning": final_state.orchestrator_reasoning,
            "workflow_status": final_state.workflow_status,
            "errors": final_state.error_messages
        }
