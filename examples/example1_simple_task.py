"""
Example 1: Simple Task Processing

Demonstrates using AgentSpawn for a simple task that doesn't require specialized agents.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orchestrator import Orchestrator
import json


def main():
    """Run simple task example."""
    
    print("=" * 80)
    print("AgentSpawn Example 1: Simple Task Processing")
    print("=" * 80)
    
    # Initialize orchestrator
    orchestrator = Orchestrator(model_name="gpt-4")
    
    # Simple task that won't require specialized agents
    simple_task = "What is the capital of France?"
    
    print(f"\nProcessing task: {simple_task}\n")
    
    # Process the task
    result = orchestrator.process_task(simple_task)
    
    # Display results
    print("Task Metadata:")
    print(f"  Complexity: {result['task_metadata']['complexity']}")
    print(f"  Keywords: {', '.join(result['task_metadata']['keywords'])}")
    print(f"  Multiple agents needed: {result['task_metadata']['requires_multiple_agents']}")
    
    print("\nOrchestrator Reasoning:")
    print(f"  {result['orchestrator_reasoning']}")
    
    print("\nSpawned Agents:")
    if result['spawned_agents']:
        for agent in result['spawned_agents']:
            print(f"  - {agent['agent_type']}: {agent['status']}")
    else:
        print("  None (direct reasoning used)")
    
    print("\nFinal Response:")
    print(f"  {result['final_response'][:200]}...")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
