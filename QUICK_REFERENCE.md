"""
Quick Reference Guide for AgentSpawn Framework
"""

# ============================================================================
# INSTALLATION
# ============================================================================
"""
1. Install dependencies:
   pip install -r requirements.txt

2. Create .env file:
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
"""

# ============================================================================
# BASIC USAGE PATTERNS
# ============================================================================

# Pattern 1: Use Orchestrator (Recommended for most tasks)
"""
from src.orchestrator import Orchestrator

orchestrator = Orchestrator(model_name="gpt-4")
result = orchestrator.process_task("Your task here")

print(result['final_response'])
print(result['task_metadata']['complexity'])
print(result['spawned_agents'])
"""

# Pattern 2: Direct Agent Usage
"""
from src.agents.data_analyst import DataAnalystAgent
from src.agents.researcher import ResearcherAgent
from src.agents.code_generator import CodeGeneratorAgent

# Data analysis
analyst = DataAnalystAgent()
result = analyst.analyze("Analyze sales data")

# Research
researcher = ResearcherAgent()
result = researcher.conduct_research("AI trends", depth="comprehensive")

# Code generation
generator = CodeGeneratorAgent()
result = generator.generate_code("Implement binary search", language="python")
"""

# Pattern 3: Check Complexity Before Processing
"""
from src.utils import extract_keywords, assess_task_complexity, detect_required_agents

task = "Your task"
keywords = extract_keywords(task)
complexity = assess_task_complexity(task, keywords)
agents = detect_required_agents(task, keywords)

print(f"Complexity: {complexity}")
print(f"Agents needed: {agents}")
"""

# Pattern 4: Work with Registry
"""
from src.agent_registry import get_registry

registry = get_registry()

# List all agents
agents = registry.list_agents()

# Get capabilities
capabilities = registry.get_agent_capabilities("data_analyst")

# Find agents by capability
code_agents = registry.get_agent_by_capability("code_generation")
"""

# ============================================================================
# COMPLEXITY LEVELS REFERENCE
# ============================================================================
"""
SIMPLE: 
  - Direct questions: "What is...?", "Who is...?"
  - Basic requests: "Define", "Explain", "Summarize"
  - Action: Direct LLM reasoning, no agents spawned

MODERATE:
  - Analysis requests: "Analyze", "Compare", "Evaluate"
  - Creation tasks: "Write", "Create", "Generate"
  - Action: Spawn detected specialized agents

COMPLEX:
  - Research-heavy: "Research", "Investigate", "Deep dive"
  - Multi-step: Multiple questions combined
  - Advanced: "Optimization", "Strategy", "Advanced"
  - Action: Spawn all detected agents, plus defaults
"""

# ============================================================================
# AGENT TYPES REFERENCE
# ============================================================================
"""
DATA_ANALYST:
  - Detects: "analyze", "data", "statistics", "metric", "trend"
  - Capabilities: statistical_analysis, trend_identification, forecasting
  - Use when: Need insights from data or metrics

RESEARCHER:
  - Detects: "research", "investigate", "explore", "background"
  - Capabilities: information_gathering, literature_review, context_analysis
  - Use when: Need comprehensive background or comparison

CODE_GENERATOR:
  - Detects: "code", "implement", "write", "algorithm", "script"
  - Capabilities: code_generation, architecture_design, optimization
  - Use when: Need code or implementation guidance
"""

# ============================================================================
# RETURN VALUE STRUCTURE
# ============================================================================
"""
orchestrator.process_task(task) returns:
{
  "final_response": str,              # Synthesized final response
  "task_metadata": {
    "task_id": str,                   # Unique task ID
    "complexity": str,                # "simple", "moderate", or "complex"
    "keywords": [str],                # Extracted keywords
    "requires_multiple_agents": bool  # True if multiple agents needed
  },
  "spawned_agents": [
    {
      "agent_type": str,              # e.g., "data_analyst"
      "agent_id": str,                # e.g., "data_analyst_abc12345"
      "status": str,                  # "initialized", "completed", "failed"
      "result": str                   # Agent's output (if completed)
    }
  ],
  "orchestrator_reasoning": str,      # Why these decisions were made
  "workflow_status": str,             # Overall workflow status
  "errors": [str]                     # Any errors encountered
}
"""

# ============================================================================
# COMMON TASKS
# ============================================================================

# Task 1: Run tests
"""
python -m pytest tests/
python -m pytest tests/test_framework.py -v
"""

# Task 2: Run examples
"""
python examples/getting_started.py
python examples/example1_simple_task.py
python examples/example2_complex_task.py
python examples/example3_direct_agents.py
"""

# Task 3: Check code quality
"""
python -m pytest tests/ --cov=src
"""

# ============================================================================
# CUSTOMIZATION
# ============================================================================

# Modify Complexity Keywords (in src/utils.py):
"""
COMPLEXITY_KEYWORDS[ComplexityLevel.SIMPLE].extend(["your_keyword"])
AGENT_KEYWORDS["data_analyst"].extend(["your_keyword"])
"""

# Register Custom Agent:
"""
from src.agent_registry import get_registry, AgentConfig
from src.state import AgentType

registry = get_registry()
config = AgentConfig(
    agent_type=AgentType.GENERAL,
    name="My Agent",
    description="Does something",
    system_prompt="You are...",
    capabilities=["capability1", "capability2"]
)
registry.register_agent(config)
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================
"""
Q: "OpenAI API key not found"
A: Create .env file and set OPENAI_API_KEY

Q: "Agent type not found"
A: Check get_registry().list_agents() to see available agents

Q: "Module not found"
A: Ensure src/ is in Python path: sys.path.insert(0, 'src')

Q: Tests failing
A: Run: python -m pytest tests/ -v to see detailed output
"""

# ============================================================================
# PERFORMANCE TIPS
# ============================================================================
"""
1. Use SIMPLE tasks when possible (no agents = faster, cheaper)
2. Cache results if processing same tasks repeatedly
3. Use appropriate temperature settings:
   - Analysis: lower (0.3-0.5)
   - Creative: higher (0.7-0.9)
4. Batch similar tasks together
5. Monitor API usage from orchestrator.process_task() results
"""

print(__doc__)
