"""
Tool Registry for AgentSpawn Framework

This module provides a registry system for external tools that agents can use.
Tools include web search, code execution, database queries, and other external services.
"""

from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
import os
from enum import Enum


class ToolType(Enum):
    """Types of tools available."""
    WEB_SEARCH = "web_search"
    CODE_EXECUTION = "code_execution"
    DATABASE_QUERY = "database_query"
    FILE_SYSTEM = "file_system"
    API_CALL = "api_call"
    CUSTOM = "custom"


@dataclass
class ToolConfig:
    """Configuration for a tool."""
    name: str
    tool_type: ToolType
    description: str
    parameters: Dict[str, Any]
    required_env_vars: List[str]
    enabled: bool = True

    def is_available(self) -> bool:
        """Check if tool is available (all required env vars present)."""
        if not self.enabled:
            return False
        return all(os.getenv(var) for var in self.required_env_vars)


class ToolResult:
    """Result from tool execution."""
    def __init__(self, success: bool, data: Any = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error


class BaseTool(ABC):
    """Abstract base class for all tools."""

    def __init__(self, config: ToolConfig):
        self.config = config
        self.validate_config()

    def validate_config(self):
        """Validate tool configuration."""
        if not self.config.is_available():
            missing_vars = [var for var in self.config.required_env_vars
                          if not os.getenv(var)]
            raise ValueError(f"Missing required environment variables: {missing_vars}")

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        pass

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def description(self) -> str:
        return self.config.description


class ToolRegistry:
    """Registry for managing tools."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._configs: Dict[str, ToolConfig] = {}

    def register_tool(self, tool: BaseTool):
        """Register a tool instance."""
        self._tools[tool.name] = tool
        self._configs[tool.name] = tool.config

    def register_config(self, config: ToolConfig, tool_class: type):
        """Register a tool configuration and its class."""
        self._configs[config.name] = config
        if config.is_available():
            try:
                tool_instance = tool_class(config)
                self._tools[config.name] = tool_instance
            except Exception as e:
                print(f"Warning: Failed to initialize tool {config.name}: {e}")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_available_tools(self) -> List[BaseTool]:
        """Get all available tools."""
        return [tool for tool in self._tools.values() if tool.config.is_available()]

    def get_tool_configs(self) -> Dict[str, ToolConfig]:
        """Get all tool configurations."""
        return self._configs.copy()

    def execute_tool(self, name: str, **kwargs) -> ToolResult:
        """Execute a tool by name."""
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(False, error=f"Tool '{name}' not found or not available")

        try:
            return tool.execute(**kwargs)
        except Exception as e:
            return ToolResult(False, error=f"Tool execution failed: {str(e)}")


# Global registry instance
_tool_registry = None

def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
        _initialize_default_tools(_tool_registry)
    return _tool_registry

def reset_tool_registry():
    """Reset the global tool registry (for testing)."""
    global _tool_registry
    _tool_registry = None

def _initialize_default_tools(registry: ToolRegistry):
    """Initialize default tools."""
    try:
        # Import here to avoid circular imports
        import importlib
        tools_module = importlib.import_module('src.tools')
        configs = tools_module.DEFAULT_TOOL_CONFIGS
        classes = tools_module.TOOL_CLASSES

        for config in configs:
            tool_class = classes.get(config.name)
            if tool_class:
                registry.register_config(config, tool_class)
    except (ImportError, AttributeError):
        # Tools module not available, skip initialization
        pass