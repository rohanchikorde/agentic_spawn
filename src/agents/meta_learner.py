"""
Meta-Learning Agent implementation.

Specialized agent for dynamic skill acquisition and adaptation to novel tasks.
Uses few-shot learning and meta-learning techniques to learn new capabilities on-the-fly.
"""

from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

try:
    import learn2learn as l2l
    import torch
    import torch.nn as nn
    META_LEARNING_AVAILABLE = True
except ImportError:
    l2l = None
    torch = None
    nn = None
    META_LEARNING_AVAILABLE = False


if META_LEARNING_AVAILABLE:
    class SimpleMetaModel(nn.Module):
        """Simple neural network for meta-learning demonstrations."""

        def __init__(self, input_size: int = 10, hidden_size: int = 64, output_size: int = 1):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(input_size, hidden_size),
                nn.ReLU(),
                nn.Linear(hidden_size, hidden_size),
                nn.ReLU(),
                nn.Linear(hidden_size, output_size)
            )

        def forward(self, x):
            return self.net(x)
else:
    SimpleMetaModel = None


class MetaLearningAgent:
    """
    Agent specialized in dynamic skill acquisition and meta-learning.

    Capabilities:
    - Few-shot learning from examples
    - Dynamic prompt generation for novel tasks
    - Meta-learning adaptation using MAML
    - Skill generalization across domains
    - On-the-fly capability expansion
    """

    def __init__(self, model: str = "gpt-4", meta_learning_enabled: bool = True):
        """
        Initialize the Meta-Learning Agent.

        Args:
            model: LLM model to use
            meta_learning_enabled: Whether to use neural meta-learning
        """
        self.model = model
        self.llm = ChatOpenAI(model=model, temperature=0.5)
        self.learned_skills: Dict[str, Dict[str, Any]] = {}
        self.meta_learning_enabled = meta_learning_enabled and META_LEARNING_AVAILABLE

        if self.meta_learning_enabled:
            self.meta_model = l2l.algorithms.MAML(SimpleMetaModel(), lr=0.01)
            self.adaptation_steps = 5
        else:
            self.meta_model = None

    def learn_from_examples(self, task_description: str, examples: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Learn a new skill from few-shot examples.

        Args:
            task_description: Description of the task/skill to learn
            examples: List of example input-output pairs

        Returns:
            Dictionary containing learned skill configuration
        """
        # Create few-shot prompt
        few_shot_prompt = self._create_few_shot_prompt(task_description, examples)

        # Generate system prompt for the new skill
        skill_prompt = self._generate_skill_prompt(task_description, few_shot_prompt)

        # Store the learned skill
        skill_id = f"learned_{len(self.learned_skills)}"
        self.learned_skills[skill_id] = {
            "description": task_description,
            "system_prompt": skill_prompt,
            "examples": examples,
            "created_at": "now"
        }

        return {
            "status": "learned",
            "skill_id": skill_id,
            "system_prompt": skill_prompt,
            "agent_type": "meta_learner"
        }

    def adapt_to_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Adapt to a novel task by generating appropriate prompts and strategies.

        Args:
            task: The novel task description
            context: Additional context information

        Returns:
            Adapted response for the task
        """
        # Analyze the task
        task_analysis = self._analyze_task(task)

        # Find relevant learned skills or create new ones
        relevant_skills = self._find_relevant_skills(task)

        if relevant_skills:
            # Use existing learned skills
            skill = relevant_skills[0]
            system_prompt = skill["system_prompt"]
        else:
            # Generate new approach
            system_prompt = self._generate_adaptive_prompt(task, task_analysis)

        # Execute the task
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=task)
        ]

        response = self.llm.invoke(messages)

        return {
            "status": "completed",
            "response": response.content,
            "task_analysis": task_analysis,
            "used_learned_skill": bool(relevant_skills),
            "agent_type": "meta_learner"
        }

    def meta_learn(self, tasks: List[Dict[str, Any]], adaptation_data: List) -> None:
        """
        Perform meta-learning adaptation using MAML.

        Args:
            tasks: List of task descriptions and examples
            adaptation_data: Neural network adaptation data
        """
        if not self.meta_learning_enabled or not self.meta_model:
            return

        for task_data in adaptation_data:
            learner = self.meta_model.clone()
            for _ in range(self.adaptation_steps):
                # Simulate adaptation on task-specific data
                prediction = learner(task_data)
                loss = nn.MSELoss()(prediction, torch.randn_like(prediction))
                learner.adapt(loss)

    def _create_few_shot_prompt(self, task_description: str, examples: List[Dict[str, str]]) -> str:
        """Create a few-shot learning prompt from examples."""
        prompt_parts = [f"Task: {task_description}\n\nExamples:"]

        for i, example in enumerate(examples, 1):
            prompt_parts.append(f"\nExample {i}:")
            prompt_parts.append(f"Input: {example.get('input', '')}")
            prompt_parts.append(f"Output: {example.get('output', '')}")

        return "\n".join(prompt_parts)

    def _generate_skill_prompt(self, task_description: str, few_shot_prompt: str) -> str:
        """Generate a system prompt for a new learned skill."""
        meta_prompt = f"""Based on the following task and examples, create a system prompt for an AI agent that can perform this task:

Task: {task_description}

Examples:
{few_shot_prompt}

Create a comprehensive system prompt that enables an AI to:
1. Understand the task requirements
2. Apply the patterns shown in examples
3. Generalize to similar but unseen cases
4. Provide high-quality, accurate responses

System Prompt:"""

        messages = [
            SystemMessage(content="You are an expert at creating AI system prompts for various tasks."),
            HumanMessage(content=meta_prompt)
        ]

        response = self.llm.invoke(messages)
        return response.content

    def _analyze_task(self, task: str) -> Dict[str, Any]:
        """Analyze a task to understand its requirements."""
        analysis_prompt = f"""Analyze the following task and provide:
1. Domain/category
2. Required skills or knowledge
3. Complexity level (simple, moderate, complex)
4. Potential approaches
5. Success criteria

Task: {task}

Analysis:"""

        messages = [
            SystemMessage(content="You are a task analysis expert."),
            HumanMessage(content=analysis_prompt)
        ]

        response = self.llm.invoke(messages)

        return {
            "task": task,
            "analysis": response.content
        }

    def _find_relevant_skills(self, task: str) -> List[Dict[str, Any]]:
        """Find learned skills relevant to the current task."""
        relevant = []
        for skill_id, skill in self.learned_skills.items():
            # Simple relevance check - can be enhanced with embeddings
            if any(keyword.lower() in task.lower() for keyword in skill["description"].split()):
                relevant.append(skill)
        return relevant

    def _generate_adaptive_prompt(self, task: str, task_analysis: Dict[str, Any]) -> str:
        """Generate an adaptive system prompt for a novel task."""
        adaptive_prompt = f"""You are an intelligent AI agent capable of adapting to novel tasks.

Task Analysis:
{task_analysis['analysis']}

Task: {task}

Approach this task by:
1. Breaking it down into manageable components
2. Applying general problem-solving strategies
3. Using logical reasoning and available knowledge
4. Providing clear, actionable solutions
5. Explaining your reasoning when appropriate

Be flexible, creative, and thorough in your approach."""

        return adaptive_prompt

    def get_learned_skills(self) -> Dict[str, Dict[str, Any]]:
        """Get all learned skills."""
        return self.learned_skills.copy()

    def forget_skill(self, skill_id: str) -> bool:
        """Remove a learned skill."""
        if skill_id in self.learned_skills:
            del self.learned_skills[skill_id]
            return True
        return False