"""
AgentSpawn agents module.

Contains implementations of specialized agents for various tasks.
"""

from agents.data_analyst import DataAnalystAgent
from agents.researcher import ResearcherAgent
from agents.code_generator import CodeGeneratorAgent

__all__ = [
    "DataAnalystAgent",
    "ResearcherAgent",
    "CodeGeneratorAgent"
]
