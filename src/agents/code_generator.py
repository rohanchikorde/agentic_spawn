"""
Code Generator Agent implementation.

Specialized agent for code generation, implementation guidance, and engineering solutions.
"""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


class CodeGeneratorAgent:
    """
    Agent specialized in code generation and software engineering tasks.
    
    Capabilities:
    - Code generation in multiple languages
    - Algorithm implementation
    - Architecture and design guidance
    - Code review and optimization
    - Documentation generation
    """
    
    def __init__(self, model: str = "gpt-4"):
        """
        Initialize the Code Generator Agent.
        
        Args:
            model: LLM model to use
        """
        self.model = model
        self.llm = ChatOpenAI(model=model, temperature=0.3)
    
    def generate_code(self, requirement: str, language: str = "python") -> Dict[str, Any]:
        """
        Generate code based on requirements.
        
        Args:
            requirement: Code requirement description
            language: Programming language (python, javascript, etc.)
            
        Returns:
            Dictionary containing generated code and metadata
        """
        system_prompt = f"""You are an expert software engineer proficient in {language}.
You excel at:
- Writing clean, production-ready code
- Following best practices and design patterns
- Creating well-documented, maintainable solutions
- Considering edge cases and error handling

Generate code that is:
1. Correct and efficient
2. Well-commented with docstrings
3. Following {language} conventions
4. Robust with error handling"""
        
        prompt = f"""Generate {language} code for the following requirement:

{requirement}

Include:
1. Main implementation
2. Error handling
3. Comments explaining key logic
4. Usage example (if applicable)
5. Any necessary imports or dependencies"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "status": "completed",
            "code": response.content,
            "agent_type": "code_generator",
            "language": language
        }
    
    def implement_algorithm(self, algorithm_spec: str, language: str = "python") -> str:
        """
        Implement a specific algorithm.
        
        Args:
            algorithm_spec: Description of the algorithm
            language: Programming language
            
        Returns:
            Implemented algorithm code
        """
        system_prompt = f"""You are an expert in algorithms and data structures.
Implement efficient algorithms in {language}."""
        
        prompt = f"""Implement the following algorithm in {language}:

{algorithm_spec}

Provide:
1. Complete, working implementation
2. Time and space complexity analysis
3. Test cases and examples
4. Edge case handling
5. Optimization notes"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def provide_architecture_guidance(self, problem: str) -> str:
        """
        Provide architectural guidance for a software problem.
        
        Args:
            problem: Problem or requirement description
            
        Returns:
            Architecture recommendation
        """
        system_prompt = """You are an expert software architect.
Provide clear, practical architectural guidance."""
        
        prompt = f"""Provide architectural guidance for the following problem:

{problem}

Cover:
1. Recommended architecture pattern
2. Component breakdown
3. Technology stack recommendations
4. Scalability considerations
5. Potential challenges and solutions"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def optimize_code(self, code: str, language: str = "python") -> str:
        """
        Optimize existing code for performance or readability.
        
        Args:
            code: Code to optimize
            language: Programming language
            
        Returns:
            Optimized code with explanation
        """
        system_prompt = f"""You are an expert {language} developer specializing in code optimization.
Analyze and improve code for performance, readability, and maintainability."""
        
        prompt = f"""Optimize the following {language} code:

```{language}
{code}
```

Provide:
1. Optimized version of the code
2. Explanation of improvements
3. Performance impact analysis
4. Any best practices applied
5. Trade-offs and considerations"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
