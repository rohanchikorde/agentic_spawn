"""
Example 6: Meta-Learning Agent Demonstration

This example demonstrates the meta-learning agent's ability to:
- Learn new skills from few-shot examples
- Adapt to novel tasks dynamically
- Generalize knowledge across different domains
"""

from src.orchestrator import Orchestrator
from src.agents.meta_learner import MetaLearningAgent


def demonstrate_meta_learning():
    """Demonstrate meta-learning capabilities."""
    print("🤖 AgentSpawn Meta-Learning Agent Demo")
    print("=" * 50)

    # Initialize meta-learning agent
    meta_agent = MetaLearningAgent(model="gpt-4")

    # Example 1: Learn a new skill - creative writing
    print("\n📚 Example 1: Learning Creative Writing Skill")
    print("-" * 40)

    writing_examples = [
        {
            "input": "Write a haiku about autumn leaves",
            "output": "Crimson leaves whisper,\nWind carries summer's farewell,\nEarth claims her blanket."
        },
        {
            "input": "Write a short poem about the ocean",
            "output": "Waves crash in rhythm,\nSalty breeze carries ancient tales,\nEndless blue mystery."
        }
    ]

    learn_result = meta_agent.learn_from_examples(
        "Write creative poetry in various forms",
        writing_examples
    )

    print(f"✅ Learned skill: {learn_result['skill_id']}")
    print(f"📝 System prompt generated for the skill")

    # Example 2: Adapt to a novel task using learned skills
    print("\n🎯 Example 2: Adapting to Novel Task")
    print("-" * 40)

    novel_task = "Write a limerick about quantum physics"
    adapt_result = meta_agent.adapt_to_task(novel_task)

    print(f"Task: {novel_task}")
    print(f"Response: {adapt_result['response'][:200]}...")

    # Example 3: Learn another skill - technical explanation
    print("\n🔧 Example 3: Learning Technical Explanation Skill")
    print("-" * 40)

    tech_examples = [
        {
            "input": "Explain how recursion works",
            "output": "Recursion is a programming technique where a function calls itself to solve a problem. Each call breaks down the problem into smaller subproblems until reaching a base case that can be solved directly."
        },
        {
            "input": "Explain cloud computing",
            "output": "Cloud computing delivers computing services over the internet, including storage, processing power, and applications. Instead of owning physical servers, users access resources on-demand from remote data centers."
        }
    ]

    tech_learn_result = meta_agent.learn_from_examples(
        "Explain technical concepts clearly and accurately",
        tech_examples
    )

    print(f"✅ Learned technical explanation skill: {tech_learn_result['skill_id']}")

    # Test technical explanation
    tech_task = "Explain how machine learning differs from traditional programming"
    tech_adapt_result = meta_agent.adapt_to_task(tech_task)

    print(f"Task: {tech_task}")
    print(f"Response: {tech_adapt_result['response'][:200]}...")

    # Show learned skills
    print("\n📊 Learned Skills Summary")
    print("-" * 40)
    skills = meta_agent.get_learned_skills()
    for skill_id, skill_info in skills.items():
        print(f"• {skill_id}: {skill_info['description']}")


def demonstrate_orchestrator_with_meta_learning():
    """Demonstrate orchestrator using meta-learning for novel tasks."""
    print("\n🎭 Example 4: Orchestrator with Meta-Learning")
    print("-" * 40)

    orchestrator = Orchestrator(model_name="gpt-4")

    # Novel task that doesn't match existing agent keywords
    novel_task = "Design a board game about sustainable energy transitions"

    print(f"Processing novel task: {novel_task}")
    result = orchestrator.process_task(novel_task)

    print(f"Complexity: {result['task_metadata']['complexity']}")
    print(f"Agents spawned: {[agent['agent_type'] for agent in result['spawned_agents']]}")
    print(f"Response preview: {result['final_response'][:300]}...")


if __name__ == "__main__":
    demonstrate_meta_learning()
    demonstrate_orchestrator_with_meta_learning()

    print("\n✨ Meta-Learning Demo Complete!")
    print("\nKey Features Demonstrated:")
    print("• Few-shot learning from examples")
    print("• Dynamic skill acquisition")
    print("• Task adaptation and generalization")
    print("• Integration with orchestrator for novel tasks")