"""
Example 2: Complex Task with Multi-Agent Orchestration

Demonstrates using AgentSpawn for a complex task that spawns multiple specialized agents.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orchestrator import Orchestrator
import json


def main():
    """Run complex task example."""
    
    print("=" * 80)
    print("AgentSpawn Example 2: Complex Task with Multi-Agent Orchestration")
    print("=" * 80)
    
    # Initialize orchestrator
    orchestrator = Orchestrator(model_name="gpt-4")
    
    # Complex task requiring multiple specialized agents
    complex_task = """
    I'm building a data analytics platform for e-commerce businesses. 
    I need to:
    1. Research best practices and latest technologies for data analytics platforms
    2. Analyze key metrics like conversion rates, customer lifetime value, and retention
    3. Generate a Python implementation for data aggregation and analysis
    
    Please provide comprehensive guidance covering all three areas.
    """
    
    print(f"\nProcessing task:\n{complex_task}\n")
    
    # Process the task
    result = orchestrator.process_task(complex_task)
    
    # Display results
    print("Task Metadata:")
    print(f"  Task ID: {result['task_metadata']['task_id']}")
    print(f"  Complexity: {result['task_metadata']['complexity']}")
    print(f"  Keywords: {', '.join(result['task_metadata']['keywords'][:8])}...")
    print(f"  Multiple agents needed: {result['task_metadata']['requires_multiple_agents']}")
    
    print("\nOrchestrator Reasoning:")
    print(f"  {result['orchestrator_reasoning']}")
    
    print("\nSpawned Agents:")
    if result['spawned_agents']:
        for agent in result['spawned_agents']:
            print(f"  - Agent ID: {agent['agent_id']}")
            print(f"    Type: {agent['agent_type']}")
            print(f"    Status: {agent['status']}")
            if agent['result']:
                print(f"    Result preview: {agent['result'][:150]}...")
    else:
        print("  None")
    
    print("\nFinal Aggregated Response:")
    print(f"  {result['final_response'][:400]}...\n")
    
    print("Workflow Status:", result['workflow_status'])
    if result['errors']:
        print("Errors encountered:")
        for error in result['errors']:
            print(f"  - {error}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
