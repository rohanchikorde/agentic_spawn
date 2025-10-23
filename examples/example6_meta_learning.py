"""
Example 6: Meta-Learning Agent Demonstration

This example demonstrates the meta-learning agent's ability to:
- Learn new skills from few-shot examples
- Adapt to novel tasks dynamically
- Generalize knowledge across different domains
"""

import time
from src.orchestrator import Orchestrator
from src.agents.meta_learner import MetaLearningAgent


def demonstrate_meta_learning():
    """Demonstrate meta-learning capabilities."""
    print("🤖 AgentSpawn Meta-Learning Agent Demo")
    print("=" * 50)

    try:
        # Initialize meta-learning agent
        print("Initializing Meta-Learning Agent...")
        meta_agent = MetaLearningAgent(model="gpt-4")
        print("✅ Meta-Learning Agent initialized")

        # Example 1: Learn a new skill - creative writing
        print("\n📚 Example 1: Learning Creative Writing Skill")
        print("-" * 40)

        writing_examples = [
            {
                "input": "Write a haiku about autumn leaves",
                "output": "Crimson leaves whisper,\nWind carries summer's farewell,\nEarth claims her blanket."
            }
        ]

        print("Learning from examples...")
        start_time = time.time()
        learn_result = meta_agent.learn_from_examples(
            "Write creative poetry in various forms",
            writing_examples
        )
        learn_time = time.time() - start_time

        print(f"✅ Learned skill: {learn_result['skill_id']} (took {learn_time:.1f}s)")
        print(f"📝 System prompt generated for the skill")

        # Example 2: Adapt to a novel task using learned skills
        print("\n🎯 Example 2: Adapting to Novel Task")
        print("-" * 40)

        novel_task = "Write a haiku about technology"
        print(f"Adapting to task: {novel_task}")

        start_time = time.time()
        adapt_result = meta_agent.adapt_to_task(novel_task)
        adapt_time = time.time() - start_time

        print(f"Response (took {adapt_time:.1f}s): {adapt_result['response'][:200]}...")

        # Show learned skills
        print("\n📊 Learned Skills Summary")
        print("-" * 40)
        skills = meta_agent.get_learned_skills()
        for skill_id, skill_info in skills.items():
            print(f"• {skill_id}: {skill_info['description']}")

        print("\n✅ Meta-Learning demonstration completed successfully!")

    except Exception as e:
        print(f"❌ Error in meta-learning demonstration: {e}")
        import traceback
        traceback.print_exc()


def demonstrate_orchestrator_with_meta_learning():
    """Demonstrate orchestrator using meta-learning for novel tasks."""
    print("\n🎭 Example 4: Orchestrator with Meta-Learning")
    print("-" * 40)

    try:
        # Disable memory to avoid checkpointer issues for demo
        print("Initializing orchestrator...")
        orchestrator = Orchestrator(model_name="gpt-4", enable_memory=False)
        print("✅ Orchestrator initialized")

        # Novel task that doesn't match existing agent keywords
        novel_task = "Design a simple board game about recycling"

        print(f"Processing novel task: {novel_task}")

        start_time = time.time()
        result = orchestrator.process_task(novel_task)
        process_time = time.time() - start_time

        print(f"✅ Task processed (took {process_time:.1f}s)")
        print(f"Complexity: {result['task_metadata'].complexity}")
        print(f"Keywords: {result['task_metadata'].keywords}")
        print(f"Requires multiple agents: {result['task_metadata'].requires_multiple_agents}")
        print(f"Agents spawned: {[agent['agent_type'] for agent in result['spawned_agents']]}")
        print(f"Response preview: {result['final_response'][:300]}...")

        print("✅ Orchestrator demonstration completed successfully!")

    except Exception as e:
        print(f"❌ Error in orchestrator demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Starting Meta-Learning Agent Demo...")
    demonstrate_meta_learning()
    demonstrate_orchestrator_with_meta_learning()

    print("\n✨ Meta-Learning Demo Complete!")
    print("\nKey Features Demonstrated:")
    print("• Few-shot learning from examples")
    print("• Dynamic skill acquisition")
    print("• Task adaptation and generalization")
    print("• Integration with orchestrator for novel tasks")


if __name__ == "__main__":
    demonstrate_meta_learning()
    demonstrate_orchestrator_with_meta_learning()

    print("\n✨ Meta-Learning Demo Complete!")
    print("\nKey Features Demonstrated:")
    print("• Few-shot learning from examples")
    print("• Dynamic skill acquisition")
    print("• Task adaptation and generalization")
    print("• Integration with orchestrator for novel tasks")