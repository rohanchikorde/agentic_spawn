"""
Example 3: Direct Agent Usage

Demonstrates direct usage of individual agents without going through the orchestrator.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.data_analyst import DataAnalystAgent
from agents.researcher import ResearcherAgent
from agents.code_generator import CodeGeneratorAgent


def example_data_analyst():
    """Example using Data Analyst Agent directly."""
    print("\n" + "=" * 80)
    print("Data Analyst Agent Example")
    print("=" * 80)
    
    analyst = DataAnalystAgent()
    
    task = """Analyze the impact of a 20% price increase on sales if elasticity is -1.2.
    Current metrics: Monthly sales $100K, Average order value $50."""
    
    result = analyst.analyze(task)
    print(f"\nAnalysis Result:\n{result['analysis'][:300]}...\n")


def example_researcher():
    """Example using Researcher Agent directly."""
    print("\n" + "=" * 80)
    print("Researcher Agent Example")
    print("=" * 80)
    
    researcher = ResearcherAgent()
    
    research_result = researcher.conduct_research(
        "Machine Learning in Production Systems",
        depth="comprehensive"
    )
    print(f"\nResearch Result:\n{research_result['research'][:300]}...\n")


def example_code_generator():
    """Example using Code Generator Agent directly."""
    print("\n" + "=" * 80)
    print("Code Generator Agent Example")
    print("=" * 80)
    
    generator = CodeGeneratorAgent()
    
    requirement = """Create a Python function that implements binary search on a sorted list.
    Include error handling and docstrings."""
    
    code_result = generator.generate_code(requirement, language="python")
    print(f"\nGenerated Code:\n{code_result['code'][:300]}...\n")


def main():
    """Run all direct agent examples."""
    print("=" * 80)
    print("AgentSpawn Example 3: Direct Agent Usage")
    print("=" * 80)
    
    try:
        example_data_analyst()
    except Exception as e:
        print(f"Data Analyst example error: {e}")
    
    try:
        example_researcher()
    except Exception as e:
        print(f"Researcher example error: {e}")
    
    try:
        example_code_generator()
    except Exception as e:
        print(f"Code Generator example error: {e}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
