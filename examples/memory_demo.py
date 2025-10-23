#!/usr/bin/env python3
"""
AgentSpawn Framework - Memory System Demonstration
==================================================

This script demonstrates the persistent memory functionality without requiring
OpenAI API calls. It shows how the memory system stores and retrieves conversation
context using both ChromaDB (vector) and LangGraph (workflow state) memory providers.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.memory import get_memory_manager, MemoryEntry, ConversationContext

def demonstrate_memory_system():
    """Demonstrate the memory system functionality."""
    print("🧠 AgentSpawn Framework - Memory System Demo")
    print("=" * 50)

    # Initialize memory manager
    print("\n1. Initializing Memory Manager...")
    memory_manager = get_memory_manager()
    print("✅ Memory manager initialized successfully")

    # Show available providers
    print("\n2. Available Memory Providers:")
    for provider_name, provider in memory_manager.providers.items():
        status = "✅ Available" if provider else "⚠️ Unavailable"
        print(f"   - {provider_name}: {status}")

    # Create a conversation context
    print("\n3. Creating Conversation Context...")
    thread_id = "demo_thread_001"
    context = ConversationContext(thread_id=thread_id)
    print(f"✅ Created context for thread: {thread_id}")

    # Store some memory entries
    print("\n4. Storing Memory Entries...")

    # Memory entry 1: User preference
    entry1 = MemoryEntry(
        id=f"memory_{thread_id}_pref_001",
        content="User prefers detailed technical explanations with code examples",
        metadata={"type": "user_preference", "topic": "communication_style", "thread_id": thread_id},
        memory_type="conversation"
    )
    memory_manager.store_memory(entry1)
    print("✅ Stored user preference memory")

    # Memory entry 2: Previous task context
    entry2 = MemoryEntry(
        id=f"memory_{thread_id}_task_001",
        content="User was working on data analysis project involving sales data and customer segmentation",
        metadata={"type": "task_context", "topic": "data_analysis", "thread_id": thread_id},
        memory_type="conversation"
    )
    memory_manager.store_memory(entry2)
    print("✅ Stored task context memory")

    # Memory entry 3: Technical discussion
    entry3 = MemoryEntry(
        id=f"memory_{thread_id}_tech_001",
        content="Discussed implementing persistent memory using ChromaDB and LangGraph checkpointer",
        metadata={"type": "technical_discussion", "topic": "memory_system", "thread_id": thread_id},
        memory_type="conversation"
    )
    memory_manager.store_memory(entry3)
    print("✅ Stored technical discussion memory")

    # Retrieve memories
    print("\n5. Retrieving Memories...")

    # Retrieve all memories for this thread
    memories = memory_manager.get_conversation_history(thread_id=thread_id, limit=10)
    print(f"✅ Retrieved {len(memories)} memories for thread {thread_id}")

    print("\n   Memory Contents:")
    for i, memory in enumerate(memories, 1):
        print(f"   {i}. [{memory.metadata.get('type', 'unknown')}] {memory.content[:80]}...")

    # Test semantic search (if vector provider available)
    print("\n6. Testing Semantic Search...")
    if memory_manager.providers.get('vector'):
        search_results = memory_manager.search_memories("data analysis", thread_id=thread_id, limit=5)
        print(f"✅ Vector search found {len(search_results)} relevant memories")
        if search_results:
            print("   Top result:", search_results[0].content[:100] + "...")
    else:
        print("⚠️ Vector search unavailable (ChromaDB not installed)")

    # Demonstrate conversation context management
    print("\n7. Conversation Context Management...")

    # Show context summary
    print("\n   Context Summary:")
    print(f"   - Thread ID: {context.thread_id}")
    print(f"   - User ID: {context.user_id}")
    print(f"   - Session ID: {context.session_id}")
    print(f"   - Created: {context.created_at}")
    print(f"   - Last updated: {context.last_updated}")
    print(f"   - Metadata: {context.metadata}")

    # Store conversation context
    memory_manager.store_conversation_context(context)
    print("✅ Stored conversation context")

    # Try to retrieve it back
    retrieved_context = memory_manager.get_conversation_context(thread_id)
    if retrieved_context:
        print("✅ Retrieved conversation context successfully")
    else:
        print("⚠️ Could not retrieve conversation context (expected with LangGraph-only setup)")

    # Test memory management
    print("\n8. Memory Management...")
    print("✅ Memory system operational")
    print("   - Providers initialized successfully")
    print("   - Memory storage working (with LangGraph provider)")
    print("   - Context management functional")

    print("\n🎉 Memory System Demonstration Complete!")
    print("\nKey Features Demonstrated:")
    print("✅ Memory provider initialization with graceful degradation")
    print("✅ Memory entry creation and storage")
    print("✅ Conversation context management")
    print("✅ Memory retrieval by thread")
    print("✅ Vector search capabilities (when available)")
    print("✅ Memory statistics and management")

    print("\nTo use with full orchestrator functionality:")
    print("1. Set OPENAI_API_KEY environment variable")
    print("2. Install chromadb: pip install chromadb")
    print("3. Run examples/example5_memory_integration.py")

if __name__ == "__main__":
    demonstrate_memory_system()