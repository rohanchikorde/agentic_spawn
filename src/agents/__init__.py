"""
AgentSpawn agents module.

Contains implementations of specialized agents for various tasks.
"""

from .data_analyst import DataAnalystAgent
from .researcher import ResearcherAgent
from .code_generator import CodeGeneratorAgent

__all__ = [
    "DataAnalystAgent",
    "ResearcherAgent",
    "CodeGeneratorAgent"
]
