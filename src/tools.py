"""
Tool Implementations for AgentSpawn Framework

This module contains implementations of various tools that agents can use:
- Web search via SerpAPI
- Code execution via Jupyter
- Database queries
- File system operations
"""

import requests
import sqlite3
import subprocess
import tempfile
import os
from typing import Dict, Any, List
from pathlib import Path

from .tool_registry import BaseTool, ToolConfig, ToolResult, ToolType


class WebSearchTool(BaseTool):
    """Web search tool using SerpAPI."""

    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.api_key = os.getenv("SERPAPI_API_KEY")
        self.base_url = "https://serpapi.com/search"

    def execute(self, query: str, num_results: int = 5) -> ToolResult:
        """Execute web search."""
        try:
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": num_results
            }

            response = requests.get(self.base_url, params=params)
            response.raise_for_status()

            data = response.json()

            # Extract organic results
            results = []
            if "organic_results" in data:
                for result in data["organic_results"][:num_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", "")
                    })

            return ToolResult(True, data={"query": query, "results": results})

        except Exception as e:
            return ToolResult(False, error=f"Web search failed: {str(e)}")


class CodeExecutionTool(BaseTool):
    """Code execution tool using subprocess."""

    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.allowed_languages = config.parameters.get("allowed_languages", ["python", "bash"])
        self.timeout = config.parameters.get("timeout", 30)

    def execute(self, code: str, language: str = "python") -> ToolResult:
        """Execute code."""
        if language not in self.allowed_languages:
            return ToolResult(False, error=f"Language '{language}' not allowed")

        try:
            if language == "python":
                # Execute Python code
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(code)
                    temp_file = f.name

                try:
                    result = subprocess.run(
                        ["python", temp_file],
                        capture_output=True,
                        text=True,
                        timeout=self.timeout
                    )

                    output = result.stdout
                    error = result.stderr

                    return ToolResult(True, data={
                        "output": output,
                        "error": error,
                        "return_code": result.returncode
                    })

                finally:
                    os.unlink(temp_file)

            elif language == "bash":
                # Execute bash commands
                result = subprocess.run(
                    ["bash", "-c", code],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )

                return ToolResult(True, data={
                    "output": result.stdout,
                    "error": result.stderr,
                    "return_code": result.returncode
                })

            else:
                return ToolResult(False, error=f"Unsupported language: {language}")

        except subprocess.TimeoutExpired:
            return ToolResult(False, error=f"Code execution timed out after {self.timeout} seconds")
        except Exception as e:
            return ToolResult(False, error=f"Code execution failed: {str(e)}")


class DatabaseQueryTool(BaseTool):
    """Database query tool for SQLite databases."""

    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.db_path = config.parameters.get("db_path", ":memory:")
        self.allowed_operations = config.parameters.get("allowed_operations", ["SELECT"])

    def execute(self, query: str, operation: str = "SELECT") -> ToolResult:
        """Execute database query."""
        if operation.upper() not in self.allowed_operations:
            return ToolResult(False, error=f"Operation '{operation}' not allowed")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # For SELECT queries, fetch results
            if operation.upper() == "SELECT":
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = cursor.fetchall()

                result_data = {
                    "columns": columns,
                    "rows": rows,
                    "row_count": len(rows)
                }

                conn.close()
                return ToolResult(True, data=result_data)

            else:
                # For other operations (INSERT, UPDATE, DELETE)
                cursor.execute(query)
                conn.commit()
                conn.close()

                return ToolResult(True, data={"affected_rows": cursor.rowcount})

        except Exception as e:
            return ToolResult(False, error=f"Database query failed: {str(e)}")


class FileSystemTool(BaseTool):
    """File system operations tool."""

    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.allowed_paths = config.parameters.get("allowed_paths", [])
        self.allowed_operations = config.parameters.get("allowed_operations", ["read", "list"])

    def _is_path_allowed(self, path: str) -> bool:
        """Check if path is allowed."""
        if not self.allowed_paths:
            return True  # Allow all if no restrictions

        abs_path = os.path.abspath(path)
        return any(abs_path.startswith(os.path.abspath(allowed)) for allowed in self.allowed_paths)

    def execute(self, operation: str, path: str, **kwargs) -> ToolResult:
        """Execute file system operation."""
        if operation not in self.allowed_operations:
            return ToolResult(False, error=f"Operation '{operation}' not allowed")

        if not self._is_path_allowed(path):
            return ToolResult(False, error=f"Path '{path}' not allowed")

        try:
            if operation == "read":
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return ToolResult(True, data={"content": content, "path": path})

            elif operation == "list":
                items = os.listdir(path)
                return ToolResult(True, data={"items": items, "path": path})

            elif operation == "write":
                content = kwargs.get("content", "")
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return ToolResult(True, data={"path": path, "written": True})

            else:
                return ToolResult(False, error=f"Unsupported operation: {operation}")

        except Exception as e:
            return ToolResult(False, error=f"File operation failed: {str(e)}")


class APICallTool(BaseTool):
    """Generic API call tool."""

    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.allowed_endpoints = config.parameters.get("allowed_endpoints", [])
        self.timeout = config.parameters.get("timeout", 30)

    def execute(self, url: str, method: str = "GET", headers: Dict = None, data: Any = None) -> ToolResult:
        """Execute API call."""
        if self.allowed_endpoints and not any(url.startswith(endpoint) for endpoint in self.allowed_endpoints):
            return ToolResult(False, error=f"Endpoint '{url}' not allowed")

        try:
            headers = headers or {}
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                json=data if isinstance(data, dict) else None,
                data=data if not isinstance(data, dict) else None,
                timeout=self.timeout
            )

            return ToolResult(True, data={
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text,
                "json": response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            })

        except Exception as e:
            return ToolResult(False, error=f"API call failed: {str(e)}")


# Tool configurations
DEFAULT_TOOL_CONFIGS = [
    ToolConfig(
        name="web_search",
        tool_type=ToolType.WEB_SEARCH,
        description="Search the web for information using SerpAPI",
        parameters={},
        required_env_vars=["SERPAPI_API_KEY"]
    ),
    ToolConfig(
        name="code_execution",
        tool_type=ToolType.CODE_EXECUTION,
        description="Execute Python or bash code",
        parameters={
            "allowed_languages": ["python", "bash"],
            "timeout": 30
        },
        required_env_vars=[]
    ),
    ToolConfig(
        name="database_query",
        tool_type=ToolType.DATABASE_QUERY,
        description="Query SQLite databases",
        parameters={
            "db_path": ":memory:",
            "allowed_operations": ["SELECT", "INSERT", "UPDATE", "DELETE"]
        },
        required_env_vars=[]
    ),
    ToolConfig(
        name="file_system",
        tool_type=ToolType.FILE_SYSTEM,
        description="Perform file system operations",
        parameters={
            "allowed_paths": [],
            "allowed_operations": ["read", "list", "write"]
        },
        required_env_vars=[]
    ),
    ToolConfig(
        name="api_call",
        tool_type=ToolType.API_CALL,
        description="Make HTTP API calls",
        parameters={
            "allowed_endpoints": [],
            "timeout": 30
        },
        required_env_vars=[]
    )
]

# Tool class mapping
TOOL_CLASSES = {
    "web_search": WebSearchTool,
    "code_execution": CodeExecutionTool,
    "database_query": DatabaseQueryTool,
    "file_system": FileSystemTool,
    "api_call": APICallTool
}