# AgentSpawn: Dynamic Multi-Agent Orchestration Framework

A production-ready Python framework for dynamic multi-agent orchestration built on LangGraph. AgentSpawn analyzes task complexity and dynamically spawns specialized agents only when needed, combining traditional code logic with LLM-based reasoning.

## 🎯 Core Concept

**Single Orchestrator Agent** analyzes incoming tasks and:
1. Assesses complexity using keyword detection and pattern matching
2. Decides which specialized agents are needed
3. Spawns only required agents for cost efficiency
4. Aggregates results into cohesive responses

This approach balances reasoning flexibility (via LLMs) with decision logic efficiency (via code-based assessment).

## 🏗️ Architecture

```
agentic_spawn/
├── src/
│   ├── orchestrator.py        # Main orchestrator with LangGraph workflow
│   ├── agent_registry.py      # Agent templates and configurations
│   ├── state.py              # State management and data structures
│   ├── utils.py              # Complexity assessment and utilities
│   ├── agents/               # Individual agent implementations
│   │   ├── data_analyst.py   # Data analysis specialist
│   │   ├── researcher.py     # Research and information gathering
│   │   └── code_generator.py # Code generation and engineering
│   └── __init__.py
├── tests/                     # Comprehensive unit tests
├── examples/                  # Usage examples
├── requirements.txt
└── README.md
```

## 📦 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd agentic_spawn
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file
OPENAI_API_KEY=your_openai_api_key
```

## 🚀 Quick Start

### Basic Usage with Orchestrator

```python
from src.orchestrator import Orchestrator

# Initialize orchestrator
orchestrator = Orchestrator(model_name="gpt-4")

# Process a task
task = "Research cloud computing trends and generate Python code for a cloud service client"
result = orchestrator.process_task(task)

# Access results
print(f"Complexity: {result['task_metadata']['complexity']}")
print(f"Agents spawned: {result['spawned_agents']}")
print(f"Response: {result['final_response']}")
```

### Direct Agent Usage

```python
from src.agents.data_analyst import DataAnalystAgent

# Use agent directly
analyst = DataAnalystAgent()
result = analyst.analyze("Analyze customer churn patterns")
print(result['analysis'])
```

## 🔍 How It Works

### 1. Complexity Assessment

The framework analyzes tasks using:
- **Keyword Detection**: Identifies domain-specific keywords
- **Pattern Matching**: Detects question count, sentence complexity
- **Classification**: Maps to SIMPLE, MODERATE, or COMPLEX

```python
from src.utils import assess_task_complexity, extract_keywords

keywords = extract_keywords(task_text)
complexity = assess_task_complexity(task_text, keywords)
# Returns: ComplexityLevel.SIMPLE | MODERATE | COMPLEX
```

### 2. Agent Detection

Automatically identifies required specialists:
```python
from src.utils import detect_required_agents

agents = detect_required_agents(task_text, keywords)
# Returns: ["data_analyst", "researcher", "code_generator"]
```

### 3. Dynamic Spawning

Spawns agents only when needed:
- **SIMPLE tasks**: Direct LLM reasoning, no agents
- **MODERATE tasks**: Spawn detected specialized agents
- **COMPLEX tasks**: Spawn all detected agents + defaults

### 4. Result Aggregation

Combines results from multiple agents into cohesive response using LLM synthesis.

## 🎭 Available Agents

### Data Analyst Agent
Specializes in data-driven analysis and metrics:
- Statistical analysis and calculations
- Trend and pattern identification
- Business metrics generation
- Anomaly detection

```python
from src.agents.data_analyst import DataAnalystAgent

analyst = DataAnalystAgent()
result = analyst.analyze("Analyze Q3 sales performance")
insights = analyst.generate_insights({"revenue": 100000, "churn": 0.05})
```

### Researcher Agent
Conducts comprehensive research:
- Information gathering and synthesis
- Source evaluation
- Comparative analysis
- Hypothesis formation

```python
from src.agents.researcher import ResearcherAgent

researcher = ResearcherAgent()
result = researcher.conduct_research("Machine Learning", depth="comprehensive")
comparison = researcher.compare_concepts(["REST API", "GraphQL"])
```

### Code Generator Agent
Generates code and engineering solutions:
- Multi-language code generation
- Algorithm implementation
- Architecture guidance
- Code optimization

```python
from src.agents.code_generator import CodeGeneratorAgent

generator = CodeGeneratorAgent()
code = generator.generate_code("Implement quicksort", language="python")
optimized = generator.optimize_code(existing_code)
```

## 📊 State Management

The framework uses a hierarchical state structure:

```python
from src.state import OrchestratorState, TaskMetadata, ComplexityLevel

# State tracks:
state = OrchestratorState(
    task_metadata=TaskMetadata(...),      # Original task info
    spawned_agents=[...],                  # Agents created
    orchestrator_reasoning="...",          # Decision process
    spawned_agent_results={...},          # Agent outputs
    workflow_status="complete"            # Process status
)
```

## 🔧 Agent Registry

Extensible registry system for agent management:

```python
from src.agent_registry import get_registry, AgentConfig, AgentRegistry

# Get global registry
registry = get_registry()

# List all agents
agents = registry.list_agents()

# Get agent capabilities
capabilities = registry.get_agent_capabilities("data_analyst")

# Find agents by capability
code_agents = registry.get_agent_by_capability("code_generation")

# Register custom agent
from src.state import AgentType
custom_config = AgentConfig(
    agent_type=AgentType.GENERAL,
    name="My Custom Agent",
    description="...",
    system_prompt="...",
    capabilities=[...]
)
registry.register_agent(custom_config)
```

## 📚 LangGraph Workflow

The orchestration workflow is built with LangGraph:

```
assess_complexity
       ↓
decide_agents
       ↓
spawn_agents
       ↓
aggregate_results
       ↓
    END
```

Each node processes state and can branch conditionally.

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_framework.py::TestUtils::test_assess_task_complexity_complex

# Run with coverage
python -m pytest --cov=src tests/
```

## 📝 Examples

### Example 1: Simple Task
```bash
python examples/example1_simple_task.py
```
Demonstrates direct reasoning without agent spawning.

### Example 2: Complex Multi-Agent Task
```bash
python examples/example2_complex_task.py
```
Shows full orchestration with multiple specialized agents.

### Example 3: Direct Agent Usage
```bash
python examples/example3_direct_agents.py
```
Demonstrates using individual agents directly.

## 🎨 Customization

### Create Custom Agent

1. Create new agent class:
```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

class CustomAgent:
    def __init__(self, model="gpt-4"):
        self.llm = ChatOpenAI(model=model)
    
    def process(self, task):
        messages = [
            SystemMessage(content="Your system prompt"),
            HumanMessage(content=task)
        ]
        return self.llm.invoke(messages).content
```

2. Register in registry:
```python
from src.agent_registry import get_registry, AgentConfig
from src.state import AgentType

registry = get_registry()
config = AgentConfig(
    agent_type=AgentType.GENERAL,
    name="Custom Agent",
    description="...",
    system_prompt="...",
    capabilities=[...]
)
registry.register_agent(config)
```

### Modify Complexity Keywords

Edit `COMPLEXITY_KEYWORDS` in `src/utils.py`:
```python
COMPLEXITY_KEYWORDS[ComplexityLevel.SIMPLE].extend(["new_keyword"])
```

## 🔐 Configuration

Environment variables in `.env`:
```env
OPENAI_API_KEY=sk-...
ORCHESTRATOR_MODEL=gpt-4
ORCHESTRATOR_TEMPERATURE=0.7
```

## 📊 Workflow Status Tracking

States throughout execution:
- `initialized`: Initial state
- `assessing`: Complexity assessment in progress
- `deciding_agents`: Making spawning decisions
- `spawning`: Agents being created
- `executing`: Agents running
- `aggregating`: Combining results
- `complete`: Workflow finished
- `failed`: Error encountered

## 🚨 Error Handling

The framework includes comprehensive error handling:

```python
result = orchestrator.process_task(task)

if result['workflow_status'] == 'failed':
    for error in result['errors']:
        print(f"Error: {error}")

for agent in result['spawned_agents']:
    if agent['status'] == 'failed':
        print(f"Agent {agent['agent_id']} failed")
```

## 📈 Performance Considerations

- **Cost Optimization**: Only spawns needed agents
- **Concurrency**: Agents can be spawned in parallel (future enhancement)
- **Caching**: Agent responses can be cached
- **Timeouts**: Configurable timeouts per agent

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for new functionality
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open Pull Request

## 📄 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

- Built with [LangGraph](https://python.langchain.com/docs/langgraph)
- Powered by [LangChain](https://www.langchain.com/)
- LLM integration via [OpenAI](https://openai.com/)

## 📞 Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/your-repo/issues)
- Check [Discussions](https://github.com/your-repo/discussions)
- Review [Documentation](./README.md)

---

**Built with ❤️ for intelligent multi-agent orchestration**
