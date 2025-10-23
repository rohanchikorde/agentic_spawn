"""
Data Analyst Agent implementation.

Specialized agent for data analysis, statistical insights, and metric computation.
"""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


class DataAnalystAgent:
    """
    Agent specialized in data analysis tasks.
    
    Capabilities:
    - Statistical analysis and calculations
    - Data aggregation and summarization
    - Trend and pattern identification
    - Anomaly detection
    - Business insights generation
    """
    
    def __init__(self, model: str = "gpt-4"):
        """
        Initialize the Data Analyst Agent.
        
        Args:
            model: LLM model to use
        """
        self.model = model
        self.llm = ChatOpenAI(model=model, temperature=0.5)
    
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
