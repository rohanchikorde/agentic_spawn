"""
Researcher Agent implementation.

Specialized agent for research tasks, information gathering, and contextual analysis.
"""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import os


class ResearcherAgent:
    """
    Agent specialized in research and information gathering tasks.
    
    Capabilities:
    - Comprehensive literature review
    - Information synthesis and summarization
    - Source evaluation and credibility assessment
    - Contextual and comparative analysis
    - Hypothesis formation and testing
    """
    
    def __init__(self, model: str = "gpt-4"):
        """
        Initialize the Researcher Agent.
        
        Args:
            model: LLM model to use
        """
        self.model = model
        
        # Check for OpenRouter API key first, fallback to OpenAI
        if os.getenv("OPENROUTER_API_KEY"):
            self.llm = ChatOpenAI(
                model=model,
                temperature=0.6,
                openai_api_key=os.getenv("OPENROUTER_API_KEY"),
                openai_api_base="https://openrouter.ai/api/v1"
            )
        else:
            self.llm = ChatOpenAI(model=model, temperature=0.6)
    
    def conduct_research(self, topic: str, depth: str = "comprehensive") -> Dict[str, Any]:
        """
        Conduct comprehensive research on a topic.
        
        Args:
            topic: Research topic
            depth: Depth of research (quick, standard, comprehensive)
            
        Returns:
            Dictionary containing research findings
        """
        system_prompt = """You are a thorough research specialist with expertise in:
- Literature review and source synthesis
- Contextual analysis and background research
- Identifying authoritative sources
- Presenting balanced, well-researched perspectives

Always cite sources when available, acknowledge limitations, and present multiple viewpoints.
Be precise and evidence-based in all claims."""
        
        depth_instructions = {
            "quick": "Provide a brief overview of the key points.",
            "standard": "Provide a balanced overview covering main aspects.",
            "comprehensive": "Provide thorough coverage including background, current state, and nuances."
        }
        
        prompt = f"""Research the following topic ({depth} depth): {topic}

{depth_instructions.get(depth, depth_instructions['standard'])}

Include:
1. Background and context
2. Current status and key findings
3. Different perspectives
4. Relevant examples
5. Potential limitations or considerations"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "status": "completed",
            "research": response.content,
            "agent_type": "researcher",
            "depth_level": depth
        }
    
    def compare_concepts(self, concepts: List[str]) -> str:
        """
        Compare multiple concepts or approaches.
        
        Args:
            concepts: List of concepts to compare
            
        Returns:
            Comparative analysis
        """
        concepts_str = "\n".join([f"- {c}" for c in concepts])
        
        system_prompt = """You are an expert researcher. Provide detailed comparative analysis
of different concepts, approaches, or theories."""
        
        prompt = f"""Compare the following concepts:

{concepts_str}

Provide:
1. Key similarities
2. Important differences
3. Pros and cons of each
4. Use cases and applicability
5. Recommendations for choosing between them"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def investigate(self, question: str) -> str:
        """
        Investigate a specific question with depth.
        
        Args:
            question: Investigation question
            
        Returns:
            Investigation findings
        """
        system_prompt = """You are an investigative researcher. Thoroughly investigate the question
and provide evidence-based findings with citations when possible."""
        
        prompt = f"""Investigate the following question: {question}

Provide:
1. Direct answer to the question
2. Supporting evidence and reasoning
3. Different interpretations or perspectives
4. Related considerations or implications
5. Sources and further reading recommendations"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
