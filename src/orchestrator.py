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
from .memory import get_memory_manager, MemoryEntry, ConversationContext


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
    - Persistent memory for conversation continuity
    """
    
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.7, enable_memory: bool = True):
        """
        Initialize the orchestrator.
        
        Args:
            model_name: LLM model to use (default: gpt-4)
            temperature: Temperature for LLM responses
            enable_memory: Whether to enable persistent memory
        """
        self.model_name = model_name
        self.temperature = temperature
        self.enable_memory = enable_memory
        
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.registry = get_registry()
        
        # Initialize memory manager
        self.memory_manager = get_memory_manager() if enable_memory else None
        
        # Build workflow with memory support
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow for orchestration with memory support.
        
        Returns:
            Configured StateGraph with memory integration
        """
        workflow = StateGraph(OrchestratorState)
        
        # Add workflow nodes
        workflow.add_node("load_memory", self.load_memory_node)
        workflow.add_node("assess_complexity", self.assess_complexity_node)
        workflow.add_node("decide_agents", self.decide_agents_node)
        workflow.add_node("spawn_agents", self.spawn_agents_node)
        workflow.add_node("aggregate_results", self.aggregate_results_node)
        workflow.add_node("store_memory", self.store_memory_node)
        
        # Add edges with memory integration
        workflow.set_entry_point("load_memory")
        workflow.add_edge("load_memory", "assess_complexity")
        workflow.add_edge("assess_complexity", "decide_agents")
        workflow.add_edge("decide_agents", "spawn_agents")
        workflow.add_edge("spawn_agents", "aggregate_results")
        workflow.add_edge("aggregate_results", "store_memory")
        workflow.add_edge("store_memory", END)
        
        # Compile with memory checkpointer if available
        compiled_workflow = workflow.compile()
        
        if self.memory_manager and self.enable_memory:
            checkpointer = self.memory_manager.get_langgraph_checkpointer()
            if checkpointer:
                compiled_workflow = workflow.compile(checkpointer=checkpointer)
        
        return compiled_workflow
    
    def load_memory_node(self, state: OrchestratorState) -> OrchestratorState:
        """
        Load relevant memory context for the current task.
        
        Args:
            state: Current orchestrator state
            
        Returns:
            Updated state with memory context
        """
        if not self.memory_manager or not self.enable_memory:
            return state
        
        try:
            thread_id = state.thread_id or f"thread_{state.task_metadata.task_id}"
            task = state.task_metadata.user_input
            
            # Get relevant context from memory
            context = self.memory_manager.get_relevant_context(thread_id, task)
            
            if context:
                state.set_memory_context(thread_id, context)
                state.orchestrator_reasoning = f"Loaded memory context for thread {thread_id}. {state.orchestrator_reasoning}"
            else:
                state.set_memory_context(thread_id, "")
                state.orchestrator_reasoning = f"No previous context found for thread {thread_id}. {state.orchestrator_reasoning}"
                
        except Exception as e:
            state.orchestrator_reasoning = f"Memory loading failed: {str(e)}. {state.orchestrator_reasoning}"
        
        return state
    
        return state
    
    def assess_complexity_node(self, state: OrchestratorState) -> OrchestratorState:
        """
        Assess the complexity of the task with memory context.
        
        Uses keyword detection and pattern matching to determine task complexity.
        Incorporates memory context for better assessment.
        
        Args:
            state: Current orchestrator state
            
        Returns:
            Updated state with complexity assessment
        """
        task = state.task_metadata.user_input
        
        # Include memory context in task analysis if available
        context_prompt = ""
        if state.conversation_context:
            context_prompt = f"\n\nPrevious conversation context:\n{state.conversation_context}"
            task = f"{task}{context_prompt}"
        
        # Extract keywords
        keywords = extract_keywords(task)
        state.task_metadata.keywords = keywords
        
        # Assess complexity
        complexity = assess_task_complexity(task, keywords)
        state.task_metadata.complexity = complexity
        
        # Generate reasoning with memory awareness
        reasoning = f"Assessed task complexity as {complexity.value}. "
        reasoning += f"Keywords identified: {', '.join(keywords[:5])}. "
        
        if state.conversation_context:
            reasoning += "Incorporated previous conversation context. "
        
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
            # If no specific agents detected, spawn meta_learner for novel tasks
            if not agents_to_spawn:
                agents_to_spawn = ["meta_learner"]
            # For very complex tasks, also consider meta_learner alongside detected agents
            elif self._is_novel_task(task, keywords):
                if "meta_learner" not in agents_to_spawn:
                    agents_to_spawn.append("meta_learner")
        
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
    
    def store_memory_node(self, state: OrchestratorState) -> OrchestratorState:
        """
        Store the conversation and results in memory for future reference.
        
        Args:
            state: Current orchestrator state
            
        Returns:
            Updated state (memory storage is side effect)
        """
        if not self.memory_manager or not self.enable_memory:
            return state
        
        try:
            thread_id = state.thread_id or f"thread_{state.task_metadata.task_id}"
            user_input = state.task_metadata.user_input
            agent_response = state.final_response
            
            # Store conversation memory
            self.memory_manager.store_conversation_memory(
                thread_id=thread_id,
                user_input=user_input,
                agent_response=agent_response,
                metadata={
                    "complexity": state.task_metadata.complexity.value,
                    "agents_spawned": len(state.spawned_agents),
                    "tools_used": len(state.tool_usage),
                    "task_id": state.task_metadata.task_id
                }
            )
            
            # Store agent results as separate memories for better retrieval
            for agent in state.spawned_agents:
                if agent.result:
                    agent_memory = MemoryEntry(
                        id=f"{thread_id}_agent_{agent.agent_id}_{datetime.now().isoformat()}",
                        content=f"Agent {agent.agent_type.value} result: {agent.result}",
                        metadata={
                            "thread_id": thread_id,
                            "agent_type": agent.agent_type.value,
                            "agent_id": agent.agent_id,
                            "task_id": state.task_metadata.task_id
                        },
                        memory_type="agent_result"
                    )
                    self.memory_manager.store_memory(agent_memory)
            
            state.orchestrator_reasoning += f"\nStored conversation and results in memory for thread {thread_id}."
            
        except Exception as e:
            state.orchestrator_reasoning += f"\nMemory storage failed: {str(e)}."
        
        return state
    
    def _execute_agent(self, agent_type: str, task: str, state: OrchestratorState) -> str:
        """
        Execute a specific agent with the given task and memory context.

        Args:
            agent_type: Type of agent to execute
            task: Task for the agent to perform
            state: Current orchestrator state for tool tracking and memory

        Returns:
            Agent's response/result
        """
        try:
            config = self.registry.get_agent_config(agent_type)
        except ValueError:
            return f"Agent type {agent_type} not found"

        # Include memory context in task if available
        enhanced_task = task
        if state.conversation_context:
            enhanced_task = f"""Previous Context:
{state.conversation_context}

Current Task: {task}

Please consider the previous context when responding to maintain continuity."""

        # Get the agent instance from registry
        agent_instance = self.registry.get_agent_instance(agent_type)
        if not agent_instance:
            # Fallback to LLM-only execution
            prompt = create_agent_prompt(agent_type, enhanced_task)
            messages = [
                SystemMessage(content=config.system_prompt),
                HumanMessage(content=prompt)
            ]
            response = self.llm.invoke(messages)
            return response.content

        # Execute agent with tool support and memory context
        try:
            if hasattr(agent_instance, 'analyze'):
                # Data analyst agent with memory context
                result = agent_instance.analyze(enhanced_task, tool_usage=state.tool_usage)
                # Add tool usage to state
                state.tool_usage.extend(result.get('tool_usage', []))
                return result.get('analysis', 'No analysis provided')
            elif hasattr(agent_instance, 'adapt_to_task'):
                # Meta-learning agent
                result = agent_instance.adapt_to_task(enhanced_task)
                return result.get('response', 'No response from meta-learner')
            else:
                # Other agents - fallback to LLM with memory context
                prompt = create_agent_prompt(agent_type, enhanced_task)
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
    
    def _is_novel_task(self, task: str, keywords: List[str]) -> bool:
        """
        Determine if a task is novel/unrecognized by checking against known agent capabilities.
        
        Args:
            task: The task description
            keywords: Extracted keywords from the task
            
        Returns:
            True if the task appears novel, False otherwise
        """
        # Get all registered agent capabilities
        all_capabilities = set()
        for agent_type in self.registry.list_agents().keys():
            try:
                capabilities = self.registry.get_agent_capabilities(agent_type)
                all_capabilities.update(capabilities)
            except:
                continue
        
        # Check if any keywords match known capabilities
        keyword_matches = any(keyword.lower() in cap.lower() for keyword in keywords for cap in all_capabilities)
        
        # If no keyword matches and task is complex, consider it novel
        return not keyword_matches
    
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
    
    def process_task(self, task: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a complete task through the orchestration workflow with memory support.
        
        Args:
            task: User's task description
            thread_id: Optional thread ID for conversation continuity
            
        Returns:
            Dictionary containing:
            - final_response: The final aggregated response
            - task_metadata: Information about the task
            - spawned_agents: List of spawned agents
            - orchestrator_reasoning: Orchestrator's reasoning process
            - memory_context: Information about memory usage
        """
        # Create initial state
        task_metadata = TaskMetadata(
            task_id=generate_agent_id("task"),
            user_input=task
        )
        
        initial_state = OrchestratorState(task_metadata=task_metadata)
        
        # Set thread ID for memory continuity
        if thread_id:
            initial_state.thread_id = thread_id
        
        # Execute workflow with config for checkpointer
        config = {}
        if thread_id:
            config["configurable"] = {"thread_id": thread_id}
        
        final_state = self.workflow.invoke(initial_state, config=config)
        
        # Return results with memory information
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
            "errors": final_state.error_messages,
            "memory_context": final_state.get_memory_context() if hasattr(final_state, 'get_memory_context') else None
        }
