"""
Utility functions for AgentSpawn framework.

Includes helpers for complexity assessment, keyword detection, and common operations.
"""

import re
import uuid
from typing import List, Dict, Set
from state import ComplexityLevel


# Keyword mappings for complexity assessment
COMPLEXITY_KEYWORDS: Dict[ComplexityLevel, List[str]] = {
    ComplexityLevel.SIMPLE: [
        "hello", "hi", "greet", "simple", "basic", "what is",
        "who is", "define", "explain briefly", "summarize"
    ],
    ComplexityLevel.MODERATE: [
        "analyze", "compare", "discuss", "evaluate", "review",
        "create", "write", "generate", "solve", "calculate",
        "implement", "develop", "design"
    ],
    ComplexityLevel.COMPLEX: [
        "research", "investigate", "deep dive", "comprehensive",
        "advanced", "optimization", "architecture", "strategy",
        "complex system", "multiple factors", "multi-step",
        "data analysis", "statistical", "algorithm"
    ]
}

# Agent specialization keywords
AGENT_KEYWORDS: Dict[str, List[str]] = {
    "data_analyst": [
        "data", "analyze", "statistics", "trend", "pattern",
        "metric", "performance", "dataset", "aggregate", "query",
        "excel", "csv", "database", "sql"
    ],
    "researcher": [
        "research", "investigate", "study", "explore", "background",
        "literature", "evidence", "sources", "information", "find",
        "discover", "web", "article", "documentation"
    ],
    "code_generator": [
        "code", "write", "implement", "function", "class", "script",
        "program", "develop", "build", "python", "javascript",
        "java", "c++", "algorithm", "library"
    ]
}


def generate_agent_id(agent_type: str) -> str:
    """Generate a unique agent ID."""
    unique_suffix = str(uuid.uuid4())[:8]
    return f"{agent_type}_{unique_suffix}"


def extract_keywords(text: str) -> List[str]:
    """
    Extract relevant keywords from text.
    
    Args:
        text: Input text to analyze
        
    Returns:
        List of identified keywords
    """
    # Convert to lowercase and split
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    
    # Filter for meaningful keywords
    keywords = [
        word for word in words
        if len(word) > 2 and word not in {'the', 'and', 'or', 'is', 'are', 'a', 'an'}
    ]
    
    return keywords


def assess_task_complexity(text: str, keywords: List[str]) -> ComplexityLevel:
    """
    Assess the complexity of a task using keyword detection and pattern matching.
    
    Args:
        text: The task description
        keywords: Pre-extracted keywords
        
    Returns:
        ComplexityLevel indicating the task complexity
    """
    text_lower = text.lower()
    keyword_set = set(keywords)
    
    complexity_scores = {
        ComplexityLevel.SIMPLE: 0,
        ComplexityLevel.MODERATE: 0,
        ComplexityLevel.COMPLEX: 0
    }
    
    # Score based on keyword matches
    for complexity, words in COMPLEXITY_KEYWORDS.items():
        for word in words:
            if word in keyword_set or word in text_lower:
                complexity_scores[complexity] += 1
    
    # Pattern-based scoring
    # Multiple sentences or questions suggest complexity
    sentence_count = len(re.split(r'[.!?]+', text)) - 1
    if sentence_count > 2:
        complexity_scores[ComplexityLevel.COMPLEX] += 1
    
    # Question marks suggest inquiry complexity
    question_count = text.count('?')
    if question_count > 1:
        complexity_scores[ComplexityLevel.COMPLEX] += 1
    
    # Determine final complexity level
    max_score = max(complexity_scores.values())
    if max_score == 0:
        return ComplexityLevel.SIMPLE
    
    for complexity, score in complexity_scores.items():
        if score == max_score:
            return complexity
    
    return ComplexityLevel.SIMPLE


def detect_required_agents(text: str, keywords: List[str]) -> List[str]:
    """
    Detect which specialized agents are needed for the task.
    
    Args:
        text: The task description
        keywords: Pre-extracted keywords
        
    Returns:
        List of required agent types (e.g., ['data_analyst', 'researcher'])
    """
    text_lower = text.lower()
    keyword_set = set(keywords)
    agent_scores: Dict[str, int] = {
        "data_analyst": 0,
        "researcher": 0,
        "code_generator": 0
    }
    
    # Score each agent type based on keyword matches
    for agent_type, agent_keywords in AGENT_KEYWORDS.items():
        for agent_keyword in agent_keywords:
            if agent_keyword in keyword_set or agent_keyword in text_lower:
                agent_scores[agent_type] += 1
    
    # Return agents with meaningful scores (threshold > 0)
    required_agents = [
        agent_type for agent_type, score in agent_scores.items()
        if score > 0
    ]
    
    return required_agents


def create_agent_prompt(agent_type: str, task: str, context: str = "") -> str:
    """
    Create a specialized prompt for a specific agent type.
    
    Args:
        agent_type: Type of agent (data_analyst, researcher, code_generator)
        task: The task to perform
        context: Additional context
        
    Returns:
        Formatted prompt for the agent
    """
    prompts = {
        "data_analyst": f"""You are a data analyst. Analyze the following task and provide insights.
Focus on patterns, metrics, and data-driven conclusions.

Task: {task}
{f"Context: {context}" if context else ""}

Provide a detailed analysis with specific insights.""",
        
        "researcher": f"""You are a research specialist. Investigate and provide comprehensive information.
Focus on background, context, and authoritative sources.

Task: {task}
{f"Context: {context}" if context else ""}

Provide thorough research findings with sources.""",
        
        "code_generator": f"""You are a software engineer. Generate code or provide implementation guidance.
Focus on best practices, efficiency, and maintainability.

Task: {task}
{f"Context: {context}" if context else ""}

Provide production-ready code or clear implementation steps."""
    }
    
    return prompts.get(agent_type, task)
