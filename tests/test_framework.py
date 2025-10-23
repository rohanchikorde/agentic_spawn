"""
Unit tests for AgentSpawn framework.

Tests for state management, utils, and registry components.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from datetime import datetime

from state import (
    OrchestratorState, TaskMetadata, SpawnedAgent, AgentType, ComplexityLevel
)
from utils import (
    extract_keywords, assess_task_complexity, detect_required_agents,
    generate_agent_id, create_agent_prompt
)
from agent_registry import AgentRegistry, get_registry, reset_registry


class TestState(unittest.TestCase):
    """Test state management classes."""
    
    def test_task_metadata_creation(self):
        """Test TaskMetadata creation."""
        metadata = TaskMetadata(
            task_id="test_1",
            user_input="Test task"
        )
        self.assertEqual(metadata.task_id, "test_1")
        self.assertEqual(metadata.user_input, "Test task")
        self.assertEqual(metadata.complexity, ComplexityLevel.SIMPLE)
    
    def test_spawned_agent_creation(self):
        """Test SpawnedAgent creation."""
        agent = SpawnedAgent(
            agent_type=AgentType.DATA_ANALYST,
            agent_id="analyst_123"
        )
        self.assertEqual(agent.agent_type, AgentType.DATA_ANALYST)
        self.assertEqual(agent.status, "initialized")
        self.assertIsNone(agent.result)
    
    def test_orchestrator_state_management(self):
        """Test OrchestratorState add and update operations."""
        metadata = TaskMetadata(task_id="test_1", user_input="Test")
        state = OrchestratorState(task_metadata=metadata)
        
        # Test adding agent
        agent = SpawnedAgent(
            agent_type=AgentType.RESEARCHER,
            agent_id="researcher_001"
        )
        state.add_agent(agent)
        self.assertEqual(len(state.spawned_agents), 1)
        
        # Test updating agent result
        state.update_agent_result("researcher_001", "Test result", "completed")
        self.assertEqual(state.spawned_agents[0].result, "Test result")
        self.assertIn("researcher_001", state.spawned_agent_results)
        
        # Test error handling
        state.add_error("Test error")
        self.assertIn("Test error", state.error_messages)
        self.assertEqual(state.workflow_status, "failed")


class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        text = "The quick brown fox jumps over the lazy dog"
        keywords = extract_keywords(text)
        
        # Should contain main nouns and adjectives
        self.assertIn("quick", keywords)
        self.assertIn("fox", keywords)
        # Should not contain articles
        self.assertNotIn("the", keywords)
    
    def test_assess_task_complexity_simple(self):
        """Test complexity assessment for simple tasks."""
        text = "What is 2+2?"
        keywords = extract_keywords(text)
        complexity = assess_task_complexity(text, keywords)
        
        self.assertEqual(complexity, ComplexityLevel.SIMPLE)
    
    def test_assess_task_complexity_moderate(self):
        """Test complexity assessment for moderate tasks."""
        text = "Write a Python function to calculate the average of numbers"
        keywords = extract_keywords(text)
        complexity = assess_task_complexity(text, keywords)
        
        self.assertEqual(complexity, ComplexityLevel.MODERATE)
    
    def test_assess_task_complexity_complex(self):
        """Test complexity assessment for complex tasks."""
        text = """Research the latest machine learning algorithms. 
        Analyze their performance metrics. 
        Compare different approaches and implement one."""
        keywords = extract_keywords(text)
        complexity = assess_task_complexity(text, keywords)
        
        self.assertEqual(complexity, ComplexityLevel.COMPLEX)
    
    def test_detect_required_agents_data_analysis(self):
        """Test agent detection for data analysis tasks."""
        text = "Analyze the sales data and identify trends"
        keywords = extract_keywords(text)
        agents = detect_required_agents(text, keywords)
        
        self.assertIn("data_analyst", agents)
    
    def test_detect_required_agents_research(self):
        """Test agent detection for research tasks."""
        text = "Research the history and impact of artificial intelligence"
        keywords = extract_keywords(text)
        agents = detect_required_agents(text, keywords)
        
        self.assertIn("researcher", agents)
    
    def test_detect_required_agents_code(self):
        """Test agent detection for code generation tasks."""
        text = "Generate Python code for a sorting algorithm"
        keywords = extract_keywords(text)
        agents = detect_required_agents(text, keywords)
        
        self.assertIn("code_generator", agents)
    
    def test_generate_agent_id(self):
        """Test agent ID generation."""
        agent_id = generate_agent_id("data_analyst")
        
        self.assertTrue(agent_id.startswith("data_analyst_"))
        self.assertEqual(len(agent_id), len("data_analyst_") + 8)
    
    def test_create_agent_prompt_data_analyst(self):
        """Test prompt creation for data analyst agent."""
        prompt = create_agent_prompt("data_analyst", "Analyze sales data")
        
        self.assertIn("data analyst", prompt.lower())
        self.assertIn("Analyze sales data", prompt)
    
    def test_create_agent_prompt_researcher(self):
        """Test prompt creation for researcher agent."""
        prompt = create_agent_prompt("researcher", "Research AI")
        
        self.assertIn("research", prompt.lower())
        self.assertIn("Research AI", prompt)
    
    def test_create_agent_prompt_code_generator(self):
        """Test prompt creation for code generator agent."""
        prompt = create_agent_prompt("code_generator", "Write Python code")
        
        self.assertIn("software engineer", prompt.lower())
        self.assertIn("Write Python code", prompt)


class TestAgentRegistry(unittest.TestCase):
    """Test agent registry functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        reset_registry()
    
    def test_registry_initialization(self):
        """Test registry initializes with default agents."""
        registry = get_registry()
        agents = registry.list_agents()
        
        self.assertIn("data_analyst", agents)
        self.assertIn("researcher", agents)
        self.assertIn("code_generator", agents)
    
    def test_get_agent_config(self):
        """Test retrieving agent configuration."""
        registry = get_registry()
        config = registry.get_agent_config("data_analyst")
        
        self.assertEqual(config.agent_type.value, "data_analyst")
        self.assertEqual(config.name, "Data Analyst")
        self.assertGreater(len(config.capabilities), 0)
    
    def test_get_agent_capabilities(self):
        """Test retrieving agent capabilities."""
        registry = get_registry()
        capabilities = registry.get_agent_capabilities("researcher")
        
        self.assertIn("information_gathering", capabilities)
        self.assertIn("literature_review", capabilities)
    
    def test_has_agent(self):
        """Test checking if agent exists."""
        registry = get_registry()
        
        self.assertTrue(registry.has_agent("data_analyst"))
        self.assertFalse(registry.has_agent("nonexistent_agent"))
    
    def test_get_agent_by_capability(self):
        """Test finding agents by capability."""
        registry = get_registry()
        agents = registry.get_agent_by_capability("code_generation")
        
        self.assertIn("code_generator", agents)
    
    def test_get_nonexistent_agent_raises_error(self):
        """Test that getting nonexistent agent raises error."""
        registry = get_registry()
        
        with self.assertRaises(ValueError):
            registry.get_agent_config("nonexistent_agent")
    
    def test_singleton_pattern(self):
        """Test that registry follows singleton pattern."""
        registry1 = get_registry()
        registry2 = get_registry()
        
        self.assertIs(registry1, registry2)


if __name__ == "__main__":
    unittest.main()
