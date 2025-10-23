"""
Example 4: Tool Integration Demo

This example demonstrates how agents can use external tools to perform actions
beyond text generation, such as web search, code execution, and database queries.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.orchestrator import Orchestrator
from src.tool_registry import get_tool_registry


def demo_tool_integration():
    """Demonstrate tool integration capabilities."""

    print("🔧 AgentSpawn Tool Integration Demo")
    print("=" * 50)

    # Initialize orchestrator
    orchestrator = Orchestrator(model_name="gpt-4")

    # Show available tools
    tool_registry = get_tool_registry()
    available_tools = tool_registry.get_available_tools()

    print(f"📋 Available Tools: {len(available_tools)}")
    for tool in available_tools:
        print(f"  • {tool.name}: {tool.description}")
    print()

    # Example 1: Data analysis with code execution
    print("🧮 Example 1: Data Analysis with Code Execution")
    print("-" * 50)

    task1 = """
    Analyze the following dataset and calculate statistical measures:
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25]

    Calculate mean, median, standard deviation, and identify outliers.
    """

    try:
        result1 = orchestrator.process_task(task1)
        print(f"Task: {task1.strip()}")
        print(f"Response: {result1['final_response'][:200]}...")
        print(f"Agents spawned: {len(result1['spawned_agents'])}")
        print(f"Complexity: {result1['task_metadata']['complexity']}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()

    # Example 2: Research task with web search
    print("🔍 Example 2: Research with Web Search")
    print("-" * 50)

    task2 = """
    Research the latest developments in AI safety and summarize the key concerns
    and proposed solutions from recent publications.
    """

    try:
        result2 = orchestrator.process_task(task2)
        print(f"Task: {task2.strip()}")
        print(f"Response: {result2['final_response'][:200]}...")
        print(f"Agents spawned: {len(result2['spawned_agents'])}")
        print(f"Complexity: {result2['task_metadata']['complexity']}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()

    # Example 3: Database analysis task
    print("💾 Example 3: Database Query Analysis")
    print("-" * 50)

    task3 = """
    Analyze a database table structure and provide recommendations for optimization.
    Query the available tables and suggest indexing strategies.
    """

    try:
        result3 = orchestrator.process_task(task3)
        print(f"Task: {task3.strip()}")
        print(f"Response: {result3['final_response'][:200]}...")
        print(f"Agents spawned: {len(result3['spawned_agents'])}")
        print(f"Complexity: {result3['task_metadata']['complexity']}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()

    # Example 4: Multi-tool task
    print("🔗 Example 4: Multi-Tool Integration")
    print("-" * 50)

    task4 = """
    Research current trends in renewable energy, analyze statistical data on solar panel efficiency,
    and generate Python code to visualize energy consumption patterns.
    """

    try:
        result4 = orchestrator.process_task(task4)
        print(f"Task: {task4.strip()}")
        print(f"Response: {result4['final_response'][:200]}...")
        print(f"Agents spawned: {len(result4['spawned_agents'])}")
        print(f"Complexity: {result4['task_metadata']['complexity']}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()

    print("✅ Tool Integration Demo Complete!")
    print("\n💡 Key Features Demonstrated:")
    print("  • Dynamic tool selection based on task requirements")
    print("  • Code execution for computational tasks")
    print("  • Web search for research tasks")
    print("  • Database queries for data analysis")
    print("  • Multi-tool coordination for complex tasks")


def demo_direct_tool_usage():
    """Demonstrate direct tool usage without full orchestration."""

    print("\n🔧 Direct Tool Usage Demo")
    print("=" * 50)

    tool_registry = get_tool_registry()

    # Test code execution tool
    print("🐍 Testing Code Execution Tool:")
    code_tool = tool_registry.get_tool("code_execution")
    if code_tool:
        code = "print('Hello from tool execution!')"
        result = code_tool.execute(code, "python")
        print(f"Code: {code}")
        print(f"Output: {result.data.get('output', 'N/A')}")
        print(f"Success: {result.success}")
    else:
        print("Code execution tool not available")
    print()

    # Test web search tool (requires API key)
    print("🌐 Testing Web Search Tool:")
    search_tool = tool_registry.get_tool("web_search")
    if search_tool:
        try:
            result = search_tool.execute("Python programming", 2)
            print(f"Search Query: Python programming")
            print(f"Results found: {len(result.data.get('results', []))}")
            print(f"Success: {result.success}")
        except Exception as e:
            print(f"Web search failed (API key needed): {e}")
    else:
        print("Web search tool not available")
    print()

    # Test database tool
    print("💾 Testing Database Tool:")
    db_tool = tool_registry.get_tool("database_query")
    if db_tool:
        result = db_tool.execute("SELECT sqlite_version()", "SELECT")
        print(f"Query: SELECT sqlite_version()")
        print(f"Success: {result.success}")
        if result.success:
            print(f"Result: {result.data}")
    else:
        print("Database tool not available")


if __name__ == "__main__":
    demo_tool_integration()
    demo_direct_tool_usage()