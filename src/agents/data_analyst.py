"""
Data Analyst Agent implementation.

Specialized agent for data analysis, statistical insights, and metric computation.
"""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import time
import os

from ..tool_registry import get_tool_registry
from ..state import ToolUsage


class DataAnalystAgent:
    """
    Agent specialized in data analysis tasks.

    Capabilities:
    - Statistical analysis and calculations
    - Data aggregation and summarization
    - Trend and pattern identification
    - Anomaly detection
    - Business insights generation
    - Tool integration for data processing
    """

    def __init__(self, model: str = "gpt-4"):
        """
        Initialize the Data Analyst Agent.

        Args:
            model: LLM model to use
        """
        self.model = model
        
        # Check for OpenRouter API key first, fallback to OpenAI
        if os.getenv("OPENROUTER_API_KEY"):
            self.llm = ChatOpenAI(
                model=model,
                temperature=0.5,
                openai_api_key=os.getenv("OPENROUTER_API_KEY"),
                openai_api_base="https://openrouter.ai/api/v1"
            )
        else:
            self.llm = ChatOpenAI(model=model, temperature=0.5)
        
        self.tool_registry = get_tool_registry()
        self.agent_id = f"data_analyst_{id(self)}"

    def analyze(self, task: str, data_context: str = "", tool_usage: List[ToolUsage] = None, memory_context: str = "") -> Dict[str, Any]:
        """
        Perform data analysis on the given task with memory context.

        Args:
            task: The analysis task
            data_context: Additional data or context
            tool_usage: List to track tool usage
            memory_context: Previous conversation context from memory

        Returns:
            Dictionary containing analysis results
        """
        tool_usage = tool_usage or []

        # Check if we need to use tools for this task
        tool_results = self._use_tools_if_needed(task, tool_usage)

        system_prompt = """You are an expert data analyst with deep expertise in:
- Statistical analysis and hypothesis testing
- Data visualization and storytelling
- Business metrics and KPIs
- Trend analysis and forecasting

You have access to various tools for data processing and analysis.
Provide detailed, data-driven insights with specific metrics and conclusions.
Always consider multiple perspectives and potential biases in the data."""

        full_task = task
        if data_context:
            full_task += f"\n\nData Context:\n{data_context}"
        
        if memory_context:
            full_task += f"\n\nPrevious Conversation Context:\n{memory_context}"

        if tool_results:
            full_task += f"\n\nTool Results:\n{self._format_tool_results(tool_results)}"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=full_task)
        ]

        response = self.llm.invoke(messages)

        return {
            "status": "completed",
            "analysis": response.content,
            "agent_type": "data_analyst",
            "tools_used": [usage.tool_name for usage in tool_usage],
            "tool_usage": tool_usage
        }

    def _use_tools_if_needed(self, task: str, tool_usage: List[ToolUsage]) -> List[ToolUsage]:
        """Determine if tools are needed and use them."""
        results = []

        # Check for database queries
        if any(keyword in task.lower() for keyword in ["query", "database", "sql", "data"]):
            db_result = self._use_database_tool(task)
            if db_result:
                results.append(db_result)

        # Check for code execution needs
        if any(keyword in task.lower() for keyword in ["calculate", "compute", "analyze", "python"]):
            code_result = self._use_code_execution_tool(task)
            if code_result:
                results.append(code_result)

        # Check for web search needs
        if any(keyword in task.lower() for keyword in ["research", "search", "find", "latest"]):
            search_result = self._use_web_search_tool(task)
            if search_result:
                results.append(search_result)

        return results

    def _use_database_tool(self, task: str) -> ToolUsage:
        """Use database tool if available."""
        db_tool = self.tool_registry.get_tool("database_query")
        if not db_tool:
            return None

        # Extract potential SQL query from task
        # This is a simplified implementation - in practice, you'd use LLM to extract queries
        start_time = time.time()

        try:
            # For demo purposes, use a simple query
            result = db_tool.execute("SELECT * FROM sqlite_master LIMIT 5", "SELECT")
            execution_time = time.time() - start_time

            tool_usage = ToolUsage(
                tool_name="database_query",
                agent_id=self.agent_id,
                parameters={"query": "SELECT * FROM sqlite_master LIMIT 5"},
                result=result.data,
                success=result.success,
                error=result.error,
                execution_time=execution_time
            )

            return tool_usage

        except Exception as e:
            execution_time = time.time() - start_time
            return ToolUsage(
                tool_name="database_query",
                agent_id=self.agent_id,
                parameters={"query": "SELECT * FROM sqlite_master LIMIT 5"},
                success=False,
                error=str(e),
                execution_time=execution_time
            )

    def _use_code_execution_tool(self, task: str) -> ToolUsage:
        """Use code execution tool if available."""
        code_tool = self.tool_registry.get_tool("code_execution")
        if not code_tool:
            return None

        # Generate simple analysis code
        code = """
import numpy as np
# Simple data analysis example
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
mean = np.mean(data)
std = np.std(data)
print(f"Mean: {mean}, Std: {std}")
"""

        start_time = time.time()

        try:
            result = code_tool.execute(code, "python")
            execution_time = time.time() - start_time

            tool_usage = ToolUsage(
                tool_name="code_execution",
                agent_id=self.agent_id,
                parameters={"code": code[:50] + "...", "language": "python"},
                result=result.data,
                success=result.success,
                error=result.error,
                execution_time=execution_time
            )

            return tool_usage

        except Exception as e:
            execution_time = time.time() - start_time
            return ToolUsage(
                tool_name="code_execution",
                agent_id=self.agent_id,
                parameters={"code": code[:50] + "...", "language": "python"},
                success=False,
                error=str(e),
                execution_time=execution_time
            )

    def _use_web_search_tool(self, task: str) -> ToolUsage:
        """Use web search tool if available."""
        search_tool = self.tool_registry.get_tool("web_search")
        if not search_tool:
            return None

        # Extract search query from task
        query = task.replace("research", "").replace("search for", "").strip()[:100]

        start_time = time.time()

        try:
            result = search_tool.execute(query=query, num_results=3)
            execution_time = time.time() - start_time

            tool_usage = ToolUsage(
                tool_name="web_search",
                agent_id=self.agent_id,
                parameters={"query": query, "num_results": 3},
                result=result.data,
                success=result.success,
                error=result.error,
                execution_time=execution_time
            )

            return tool_usage

        except Exception as e:
            execution_time = time.time() - start_time
            return ToolUsage(
                tool_name="web_search",
                agent_id=self.agent_id,
                parameters={"query": query, "num_results": 3},
                success=False,
                error=str(e),
                execution_time=execution_time
            )

    def _format_tool_results(self, tool_usage: List[ToolUsage]) -> str:
        """Format tool results for inclusion in prompts."""
        formatted = []
        for usage in tool_usage:
            if usage.success and usage.result:
                formatted.append(f"Tool: {usage.tool_name}")
                if isinstance(usage.result, dict):
                    for key, value in usage.result.items():
                        formatted.append(f"  {key}: {value}")
                else:
                    formatted.append(f"  Result: {usage.result}")
            else:
                formatted.append(f"Tool: {usage.tool_name} - Failed: {usage.error}")

        return "\n".join(formatted)
    
    def analyze(self, task: str, data_context: str = "") -> Dict[str, Any]:
        """
        Perform data analysis on the given task.
        
        Args:
            task: The analysis task
            data_context: Additional data or context
            
        Returns:
            Dictionary containing analysis results
        """
        system_prompt = """You are an expert data analyst with deep expertise in:
- Statistical analysis and hypothesis testing
- Data visualization and storytelling
- Business metrics and KPIs
- Trend analysis and forecasting

Provide detailed, data-driven insights with specific metrics and conclusions.
Always consider multiple perspectives and potential biases in the data."""
        
        full_task = task
        if data_context:
            full_task += f"\n\nData Context:\n{data_context}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=full_task)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "status": "completed",
            "analysis": response.content,
            "agent_type": "data_analyst"
        }
    
    def generate_insights(self, metrics: Dict[str, float]) -> str:
        """
        Generate business insights from metric data.
        
        Args:
            metrics: Dictionary of metric names and values
            
        Returns:
            Generated insights
        """
        metrics_str = "\n".join([f"- {k}: {v}" for k, v in metrics.items()])
        
        system_prompt = """You are a business intelligence expert. Analyze the provided metrics
and generate actionable insights for stakeholders."""
        
        prompt = f"""Analyze these metrics and provide business insights:

{metrics_str}

Focus on:
1. Key performance indicators
2. Areas of concern
3. Opportunities for improvement
4. Recommended actions"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
