#!/usr/bin/env python3
"""
AgentSpawn Framework - Memory Integration Example

This example demonstrates the persistent memory capabilities of the AgentSpawn framework,
showing how agents can maintain context across multiple interactions.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.orchestrator import Orchestrator
import dotenv

# Load environment variables
dotenv.load_dotenv()


def demonstrate_memory_integration():
    """Demonstrate persistent memory across multiple conversations."""

    print("🧠 AgentSpawn Framework - Memory Integration Demo")
    print("=" * 60)

    # Initialize orchestrator with memory enabled
    orchestrator = Orchestrator(model_name="gpt-4", enable_memory=True)

    # Use a consistent thread ID for conversation continuity
    thread_id = "demo_conversation_001"

    print(f"Using thread ID: {thread_id}")
    print()

    # First interaction - Initial data analysis request
    print("🔄 Interaction 1: Initial data analysis request")
    print("-" * 50)

    task1 = """
    Analyze the sales data for our e-commerce platform. We have customer purchase data
    from the last quarter. Please provide insights on:
    1. Top-selling products
    2. Customer segmentation
    3. Revenue trends
    """

    print(f"User: {task1.strip()}")

    result1 = orchestrator.process_task(task1, thread_id=thread_id)

    print(f"Agent: {result1['final_response'][:200]}...")
    print(f"Memory stored for thread: {thread_id}")
    print()

    # Second interaction - Follow-up question using memory
    print("🔄 Interaction 2: Follow-up analysis using memory context")
    print("-" * 50)

    task2 = """
    Based on the previous analysis, what recommendations do you have for
    improving customer retention and increasing average order value?
    """

    print(f"User: {task2.strip()}")

    result2 = orchestrator.process_task(task2, thread_id=thread_id)

    print(f"Agent: {result2['final_response'][:200]}...")
    print(f"Memory context loaded and used for continuity")
    print()

    # Third interaction - Specific data request
    print("🔄 Interaction 3: Specific data analysis request")
    print("-" * 50)

    task3 = """
    Can you calculate the customer lifetime value (CLV) for our top 10% of customers?
    Use the data from our previous discussions.
    """

    print(f"User: {task3.strip()}")

    result3 = orchestrator.process_task(task3, thread_id=thread_id)

    print(f"Agent: {result3['final_response'][:200]}...")
    print(f"Complete conversation history maintained")
    print()

    # Show memory context information
    print("📊 Memory Context Summary")
    print("-" * 50)

    if result3.get('memory_context'):
        memory_info = result3['memory_context']
        print(f"Thread ID: {memory_info.get('thread_id', 'N/A')}")
        print(f"Context Available: {'Yes' if memory_info.get('conversation_context') else 'No'}")
        print(f"Relevant Memories: {len(memory_info.get('relevant_memories', []))}")

        if memory_info.get('conversation_context'):
            print(f"Context Length: {len(memory_info['conversation_context'])} characters")
    else:
        print("Memory context information not available")

    print()

    # Demonstrate memory retrieval
    print("🔍 Memory Retrieval Demo")
    print("-" * 50)

    from src.memory import get_memory_manager

    memory_manager = get_memory_manager()

    # Get conversation history
    history = memory_manager.get_conversation_history(thread_id, limit=5)

    print(f"Retrieved {len(history)} conversation entries from memory:")
    for i, entry in enumerate(history, 1):
        role = entry.metadata.get('role', 'unknown')
        content_preview = entry.content[:100] + "..." if len(entry.content) > 100 else entry.content
        print(f"{i}. {role.title()}: {content_preview}")

    print()

    # Demonstrate semantic search
    print("🔎 Semantic Memory Search")
    print("-" * 50)

    search_query = "customer retention recommendations"
    relevant_memories = memory_manager.retrieve_memories(search_query, limit=3)

    print(f"Search query: '{search_query}'")
    print(f"Found {len(relevant_memories)} relevant memories:")

    for i, memory in enumerate(relevant_memories, 1):
        content_preview = memory.content[:150] + "..." if len(memory.content) > 150 else memory.content
        print(f"{i}. {content_preview}")

    print()

    print("✅ Memory Integration Demo Complete!")
    print("The framework now supports:")
    print("• Persistent conversation context across interactions")
    print("• Semantic memory retrieval for relevant information")
    print("• Vector-based storage for efficient similarity search")
    print("• LangGraph state persistence for workflow continuity")


def demonstrate_memory_configuration():
    """Show different memory configuration options."""

    print("\n⚙️ Memory Configuration Options")
    print("=" * 60)

    # Example configurations
    configs = {
        "Default ChromaDB": {
            "vector_store": {
                "provider": "chroma",
                "collection_name": "agent_memory",
                "persist_directory": "./chroma_db"
            }
        },

        "Custom Memory Location": {
            "vector_store": {
                "provider": "chroma",
                "collection_name": "custom_memory",
                "persist_directory": "/path/to/custom/db"
            }
        },

        "Memory Disabled": {
            "enable_persistence": False
        }
    }

    for config_name, config in configs.items():
        print(f"\n{config_name}:")
        print(f"  {config}")

    print("\nTo use custom configuration:")
    print("  memory_manager = get_memory_manager(config=custom_config)")


if __name__ == "__main__":
    # Check for required API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key in the .env file")
        sys.exit(1)

    try:
        demonstrate_memory_integration()
        demonstrate_memory_configuration()

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Please install required dependencies:")
        print("  pip install chromadb langchain-community")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)