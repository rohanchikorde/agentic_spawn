"""
Getting Started Guide for AgentSpawn Framework

This script demonstrates the key concepts and usage patterns of AgentSpawn.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orchestrator import Orchestrator
from agent_registry import get_registry
from utils import assess_task_complexity, detect_required_agents, extract_keywords
from state import ComplexityLevel


def demo_complexity_assessment():
    """Demonstrate task complexity assessment."""
    print("\n" + "=" * 80)
    print("DEMO 1: Task Complexity Assessment")
    print("=" * 80)
    
    test_tasks = [
        "What is the capital of France?",
        "Write a Python function to calculate fibonacci numbers",
        """Conduct a comprehensive market analysis including:
           1. Competitor research and positioning
           2. Industry trend analysis
           3. Customer sentiment analysis
           4. Python implementation for market data aggregation"""
    ]
    
    for task in test_tasks:
        print(f"\nTask: {task[:50]}...")
        keywords = extract_keywords(task)
        complexity = assess_task_complexity(task, keywords)
        print(f"Complexity: {complexity.value}")
        print(f"Keywords: {keywords[:5]}")


def demo_agent_detection():
    """Demonstrate agent detection."""
    print("\n" + "=" * 80)
    print("DEMO 2: Agent Detection")
    print("=" * 80)
    
    test_tasks = [
        "Analyze our monthly sales data to identify trends",
        "Research the history and future of artificial intelligence",
        "Generate production-ready Python code for a REST API",
        "Analyze customer data, research market trends, and generate API code"
    ]
    
    for task in test_tasks:
        print(f"\nTask: {task[:50]}...")
        keywords = extract_keywords(task)
        agents = detect_required_agents(task, keywords)
        print(f"Detected Agents: {agents if agents else 'None (direct reasoning)'}")


def demo_registry():
    """Demonstrate agent registry."""
    print("\n" + "=" * 80)
    print("DEMO 3: Agent Registry")
    print("=" * 80)
    
    registry = get_registry()
    
    print("\nRegistered Agents:")
    for agent_type, config in registry.list_agents().items():
        print(f"\n  {config.name}:")
        print(f"    Type: {agent_type}")
        print(f"    Description: {config.description}")
        print(f"    Capabilities: {', '.join(config.capabilities[:3])}...")


def demo_orchestrator_workflow():
    """Demonstrate orchestrator workflow (requires API key)."""
    print("\n" + "=" * 80)
    print("DEMO 4: Orchestrator Workflow")
    print("=" * 80)
    
    print("\n⚠️  This demo requires a valid OPENAI_API_KEY in .env")
    print("The orchestrator processes tasks through this workflow:")
    print("""
    1. assess_complexity: Analyze task keywords and patterns
    2. decide_agents: Determine which agents to spawn
    3. spawn_agents: Create and execute specialized agents
    4. aggregate_results: Combine agent outputs into final response
    """)
    
    print("\nExample workflow:")
    task = "Research AI trends and generate Python code for ML"
    keywords = extract_keywords(task)
    complexity = assess_task_complexity(task, keywords)
    agents = detect_required_agents(task, keywords)
    
    print(f"  Input: {task}")
    print(f"  → Complexity: {complexity.value}")
    print(f"  → Agents to spawn: {agents}")
    print(f"  → Final Response: [synthesized from agent results]")


def demo_state_management():
    """Demonstrate state management."""
    print("\n" + "=" * 80)
    print("DEMO 5: State Management")
    print("=" * 80)
    
    from state import OrchestratorState, TaskMetadata, SpawnedAgent, AgentType
    from utils import generate_agent_id
    
    print("\nCreating orchestrator state...")
    
    # Create metadata
    metadata = TaskMetadata(
        task_id=generate_agent_id("task"),
        user_input="Analyze sales data and generate reports"
    )
    
    # Create initial state
    state = OrchestratorState(task_metadata=metadata)
    print(f"  Task ID: {state.task_metadata.task_id}")
    print(f"  Initial Status: {state.workflow_status}")
    
    # Spawn agents
    for i, agent_type in enumerate(["data_analyst", "researcher"], 1):
        agent = SpawnedAgent(
            agent_type=AgentType(agent_type),
            agent_id=generate_agent_id(agent_type)
        )
        state.add_agent(agent)
    
    print(f"  Spawned Agents: {len(state.spawned_agents)}")
    
    # Update results
    for i, agent in enumerate(state.spawned_agents):
        state.update_agent_result(agent.agent_id, f"Result from {agent.agent_type.value}", "completed")
    
    print(f"  Completed: {len(state.spawned_agent_results)}")
    print(f"  Final Status: {state.workflow_status}")


def main():
    """Run all demonstrations."""
    print("=" * 80)
    print("AgentSpawn Framework - Getting Started Guide")
    print("=" * 80)
    print("\nThis guide demonstrates the core concepts of AgentSpawn:")
    print("1. Task Complexity Assessment")
    print("2. Agent Detection")
    print("3. Agent Registry")
    print("4. Orchestrator Workflow")
    print("5. State Management")
    
    try:
        demo_complexity_assessment()
    except Exception as e:
        print(f"Error in demo 1: {e}")
    
    try:
        demo_agent_detection()
    except Exception as e:
        print(f"Error in demo 2: {e}")
    
    try:
        demo_registry()
    except Exception as e:
        print(f"Error in demo 3: {e}")
    
    try:
        demo_orchestrator_workflow()
    except Exception as e:
        print(f"Error in demo 4: {e}")
    
    try:
        demo_state_management()
    except Exception as e:
        print(f"Error in demo 5: {e}")
    
    print("\n" + "=" * 80)
    print("Getting Started Complete!")
    print("=" * 80)
    print("\nNext Steps:")
    print("1. Set up .env file with your OPENAI_API_KEY")
    print("2. Run examples: python examples/example1_simple_task.py")
    print("3. Review test suite: python -m pytest tests/")
    print("4. Read full documentation: README.md")
    print("\n")


if __name__ == "__main__":
    main()
