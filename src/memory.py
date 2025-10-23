"""
Memory management system for AgentSpawn framework.

Provides persistent memory capabilities using vector databases and LangGraph
state persistence for maintaining context across sessions.
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass, field

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

from langgraph.checkpoint.memory import MemorySaver
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import dotenv

# Load environment variables
dotenv.load_dotenv()


@dataclass
class MemoryEntry:
    """Represents a single memory entry."""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    memory_type: str = "conversation"  # conversation, agent_result, tool_usage, etc.


@dataclass
class ConversationContext:
    """Context for a conversation thread."""
    thread_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MemoryProvider(ABC):
    """Abstract base class for memory providers."""

    @abstractmethod
    def store_memory(self, entry: MemoryEntry) -> bool:
        """Store a memory entry."""
        pass

    @abstractmethod
    def retrieve_memories(self, query: str, limit: int = 5, metadata_filter: Optional[Dict] = None) -> List[MemoryEntry]:
        """Retrieve relevant memories based on semantic search."""
        pass

    @abstractmethod
    def get_conversation_history(self, thread_id: str, limit: int = 10) -> List[MemoryEntry]:
        """Get conversation history for a thread."""
        pass

    @abstractmethod
    def store_conversation_context(self, context: ConversationContext) -> bool:
        """Store conversation context."""
        pass

    @abstractmethod
    def get_conversation_context(self, thread_id: str) -> Optional[ConversationContext]:
        """Retrieve conversation context."""
        pass


class ChromaMemoryProvider(MemoryProvider):
    """ChromaDB-based memory provider for vector storage."""

    def __init__(self, collection_name: str = "agent_memory", persist_directory: str = "./chroma_db"):
        if not CHROMA_AVAILABLE:
            raise ImportError("ChromaDB is required for ChromaMemoryProvider. Install with: pip install chromadb")

        self.collection_name = collection_name
        self.persist_directory = persist_directory

        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Create or get collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except ValueError:
            self.collection = self.client.create_collection(name=collection_name)

        # LangChain Chroma wrapper for semantic search
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embeddings
        )

    def store_memory(self, entry: MemoryEntry) -> bool:
        """Store a memory entry in ChromaDB."""
        try:
            # Prepare metadata
            metadata = entry.metadata.copy()
            metadata.update({
                "timestamp": entry.timestamp.isoformat(),
                "memory_type": entry.memory_type,
                "id": entry.id
            })

            # Add to ChromaDB
            self.collection.add(
                documents=[entry.content],
                metadatas=[metadata],
                ids=[entry.id]
            )

            return True
        except Exception as e:
            print(f"Error storing memory: {e}")
            return False

    def retrieve_memories(self, query: str, limit: int = 5, metadata_filter: Optional[Dict] = None) -> List[MemoryEntry]:
        """Retrieve relevant memories using semantic search."""
        try:
            # Build filter
            where_clause = metadata_filter or {}

            # Search using LangChain wrapper for better semantic search
            docs = self.vectorstore.similarity_search(
                query=query,
                k=limit,
                filter=where_clause if where_clause else None
            )

            memories = []
            for doc in docs:
                metadata = doc.metadata
                memory = MemoryEntry(
                    id=metadata.get("id", ""),
                    content=doc.page_content,
                    metadata={k: v for k, v in metadata.items() if k not in ["id", "timestamp", "memory_type"]},
                    timestamp=datetime.fromisoformat(metadata.get("timestamp", datetime.now().isoformat())),
                    memory_type=metadata.get("memory_type", "conversation")
                )
                memories.append(memory)

            return memories
        except Exception as e:
            print(f"Error retrieving memories: {e}")
            return []

    def get_conversation_history(self, thread_id: str, limit: int = 10) -> List[MemoryEntry]:
        """Get conversation history for a thread."""
        try:
            # Query for conversation memories with this thread_id
            results = self.collection.get(
                where={"thread_id": thread_id, "memory_type": "conversation"},
                limit=limit
            )

            memories = []
            for i, doc in enumerate(results["documents"]):
                metadata = results["metadatas"][i]
                memory = MemoryEntry(
                    id=results["ids"][i],
                    content=doc,
                    metadata={k: v for k, v in metadata.items() if k not in ["timestamp", "memory_type"]},
                    timestamp=datetime.fromisoformat(metadata.get("timestamp", datetime.now().isoformat())),
                    memory_type="conversation"
                )
                memories.append(memory)

            # Sort by timestamp
            memories.sort(key=lambda x: x.timestamp)
            return memories
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []

    def store_conversation_context(self, context: ConversationContext) -> bool:
        """Store conversation context."""
        try:
            context_data = {
                "thread_id": context.thread_id,
                "user_id": context.user_id,
                "session_id": context.session_id,
                "created_at": context.created_at.isoformat(),
                "last_updated": context.last_updated.isoformat(),
                "metadata": json.dumps(context.metadata)
            }

            # Store as a special memory entry
            context_memory = MemoryEntry(
                id=f"context_{context.thread_id}",
                content=f"Conversation context for thread {context.thread_id}",
                metadata=context_data,
                memory_type="context"
            )

            return self.store_memory(context_memory)
        except Exception as e:
            print(f"Error storing conversation context: {e}")
            return False

    def get_conversation_context(self, thread_id: str) -> Optional[ConversationContext]:
        """Retrieve conversation context."""
        try:
            results = self.collection.get(
                where={"thread_id": thread_id, "memory_type": "context"},
                limit=1
            )

            if not results["documents"]:
                return None

            metadata = results["metadatas"][0]
            return ConversationContext(
                thread_id=metadata["thread_id"],
                user_id=metadata.get("user_id"),
                session_id=metadata.get("session_id"),
                created_at=datetime.fromisoformat(metadata["created_at"]),
                last_updated=datetime.fromisoformat(metadata["last_updated"]),
                metadata=json.loads(metadata.get("metadata", "{}"))
            )
        except Exception as e:
            print(f"Error getting conversation context: {e}")
            return None


class LangGraphMemoryProvider(MemoryProvider):
    """LangGraph-based memory provider for workflow state persistence."""

    def __init__(self):
        self.checkpointer = MemorySaver()
        self.memory_store = {}  # Simple in-memory store for conversation contexts

    def store_memory(self, entry: MemoryEntry) -> bool:
        """Store memory entry (not directly applicable for LangGraph checkpointer)."""
        # LangGraph checkpointer handles state persistence automatically
        # This method is here for interface compatibility
        return True

    def retrieve_memories(self, query: str, limit: int = 5, metadata_filter: Optional[Dict] = None) -> List[MemoryEntry]:
        """Retrieve memories (not directly supported by LangGraph checkpointer)."""
        # LangGraph checkpointer doesn't support semantic search
        # This would need to be implemented with a separate vector store
        return []

    def get_conversation_history(self, thread_id: str, limit: int = 10) -> List[MemoryEntry]:
        """Get conversation history from LangGraph checkpoints."""
        try:
            # Get all checkpoints for this thread
            config = {"configurable": {"thread_id": thread_id}}
            checkpoints = []

            # LangGraph MemorySaver doesn't have a direct way to list all checkpoints
            # This is a simplified implementation
            if thread_id in self.memory_store:
                return self.memory_store[thread_id][-limit:]
            return []
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []

    def store_conversation_context(self, context: ConversationContext) -> bool:
        """Store conversation context."""
        try:
            if context.thread_id not in self.memory_store:
                self.memory_store[context.thread_id] = []
            # Store context in memory
            return True
        except Exception as e:
            print(f"Error storing conversation context: {e}")
            return False

    def get_conversation_context(self, context: ConversationContext) -> Optional[ConversationContext]:
        """Retrieve conversation context."""
        try:
            if context.thread_id in self.memory_store:
                return self.memory_store[context.thread_id][-1]  # Return latest
            return None
        except Exception as e:
            print(f"Error getting conversation context: {e}")
            return None


class MemoryManager:
    """Central memory management system coordinating multiple memory providers."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.providers = {}

        # Initialize providers
        self._initialize_providers()

    def _default_config(self) -> Dict[str, Any]:
        """Get default memory configuration."""
        return {
            "vector_store": {
                "provider": "chroma",
                "collection_name": "agent_memory",
                "persist_directory": "./chroma_db"
            },
            "langgraph": {
                "enabled": True
            },
            "enable_persistence": True
        }

    def _initialize_providers(self):
        """Initialize memory providers based on configuration."""
        # Initialize vector store provider
        vector_config = self.config.get("vector_store", {})
        if vector_config.get("provider") == "chroma":
            try:
                self.providers["vector"] = ChromaMemoryProvider(
                    collection_name=vector_config.get("collection_name", "agent_memory"),
                    persist_directory=vector_config.get("persist_directory", "./chroma_db")
                )
                print("✅ ChromaDB memory provider initialized")
            except ImportError:
                print("⚠️ ChromaDB not available, vector memory disabled")
            except Exception as e:
                print(f"⚠️ Failed to initialize ChromaDB: {e}")

        # Initialize LangGraph provider
        if self.config.get("langgraph", {}).get("enabled", True):
            self.providers["langgraph"] = LangGraphMemoryProvider()
            print("✅ LangGraph memory provider initialized")

    def store_memory(self, entry: MemoryEntry, provider: str = "vector") -> bool:
        """Store a memory entry using specified provider."""
        if provider not in self.providers:
            print(f"⚠️ Memory provider '{provider}' not available")
            return False

        return self.providers[provider].store_memory(entry)

    def retrieve_memories(self, query: str, limit: int = 5, provider: str = "vector",
                         metadata_filter: Optional[Dict] = None) -> List[MemoryEntry]:
        """Retrieve memories using specified provider."""
        if provider not in self.providers:
            print(f"⚠️ Memory provider '{provider}' not available")
            return []

        return self.providers[provider].retrieve_memories(query, limit, metadata_filter)

    def get_conversation_history(self, thread_id: str, limit: int = 10, provider: str = "vector") -> List[MemoryEntry]:
        """Get conversation history for a thread."""
        if provider not in self.providers:
            print(f"⚠️ Memory provider '{provider}' not available")
            return []

        return self.providers[provider].get_conversation_history(thread_id, limit)

    def store_conversation_context(self, context: ConversationContext, provider: str = "vector") -> bool:
        """Store conversation context."""
        if provider not in self.providers:
            print(f"⚠️ Memory provider '{provider}' not available")
            return False

        return self.providers[provider].store_conversation_context(context)

    def get_conversation_context(self, thread_id: str, provider: str = "vector") -> Optional[ConversationContext]:
        """Retrieve conversation context."""
        if provider not in self.providers:
            print(f"⚠️ Memory provider '{provider}' not available")
            return None

        return self.providers[provider].get_conversation_context(thread_id)

    def get_langgraph_checkpointer(self) -> Optional[MemorySaver]:
        """Get LangGraph checkpointer for workflow persistence."""
        if "langgraph" in self.providers:
            return self.providers["langgraph"].checkpointer
        return None

    def store_conversation_memory(self, thread_id: str, user_input: str, agent_response: str,
                                metadata: Optional[Dict] = None):
        """Store a conversation turn in memory."""
        # Store user input
        user_memory = MemoryEntry(
            id=f"{thread_id}_user_{datetime.now().isoformat()}",
            content=user_input,
            metadata={"thread_id": thread_id, "role": "user", **(metadata or {})},
            memory_type="conversation"
        )
        self.store_memory(user_memory)

        # Store agent response
        agent_memory = MemoryEntry(
            id=f"{thread_id}_agent_{datetime.now().isoformat()}",
            content=agent_response,
            metadata={"thread_id": thread_id, "role": "agent", **(metadata or {})},
            memory_type="conversation"
        )
        self.store_memory(agent_memory)

    def get_relevant_context(self, thread_id: str, current_query: str, limit: int = 3) -> str:
        """Get relevant conversation context for the current query."""
        # Get recent conversation history
        history = self.get_conversation_history(thread_id, limit=limit*2)

        if not history:
            return ""

        # Get semantically similar memories
        relevant_memories = self.retrieve_memories(current_query, limit=limit)

        # Combine and format context
        context_parts = []

        if history:
            context_parts.append("Recent conversation:")
            for memory in history[-limit:]:  # Last N messages
                role = memory.metadata.get("role", "unknown")
                context_parts.append(f"{role.title()}: {memory.content}")

        if relevant_memories:
            context_parts.append("\nRelevant past context:")
            for memory in relevant_memories:
                if memory not in history:  # Avoid duplicates
                    context_parts.append(f"Past: {memory.content}")

        return "\n".join(context_parts)


# Global memory manager instance
_memory_manager = None

def get_memory_manager(config: Optional[Dict[str, Any]] = None) -> MemoryManager:
    """Get the global memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager(config)
    return _memory_manager