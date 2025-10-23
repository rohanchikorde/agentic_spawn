# AgentSpawn: Dynamic Multi-Agent Orchestration Framework

A production-ready Python framework for dynamic multi-agent orchestration built on LangGraph. AgentSpawn analyzes task complexity and dynamically spawns specialized agents only when needed, combining traditional code logic with LLM-based reasoning.

## 🎯 Core Concept

**Single Orchestrator Agent** analyzes incoming tasks and:
1. Assesses complexity using keyword detection and pattern matching
2. Decides which specialized agents are needed
3. Spawns only required agents for cost efficiency
4. Aggregates results into cohesive responses

This approach balances reasoning flexibility (via LLMs) with decision logic efficiency (via code-based assessment).

## 🔧 Tool Integration

**External Tool Support** enables agents to perform actions beyond text generation:
- **Web Search**: Query external APIs (SerpAPI) for real-time information
- **Code Execution**: Run Python/bash scripts with timeout and security controls
- **Database Queries**: Execute SQL queries on SQLite databases
- **File System Operations**: Safe file operations with path restrictions
- **API Calls**: Make HTTP requests to external services

Tools are automatically selected based on task analysis and integrated into agent workflows.

## 🧠 Persistent Memory System

**Long-term Memory** enables conversation continuity and context retention across sessions:
- **Vector Database Storage**: ChromaDB for semantic memory and similarity search
- **Conversation Context**: Maintains thread-based conversation history
- **LangGraph State Persistence**: Workflow state preservation using LangGraph checkpointers
- **Intelligent Retrieval**: Context-aware memory retrieval for relevant information
- **Multi-turn Conversations**: Seamless continuity across multiple interactions

Memory automatically stores conversation history, agent results, and tool usage for future reference.

## 🏗️ Architecture

```
agentic_spawn/
├── src/
│   ├── orchestrator.py        # Main orchestrator with LangGraph workflow
│   ├── agent_registry.py      # Agent templates and configurations
│   ├── state.py              # State management and data structures
│   ├── utils.py              # Complexity assessment and utilities
│   ├── memory.py             # Persistent memory system (ChromaDB + LangGraph)
│   ├── tool_registry.py      # External tool management system
│   ├── tools.py              # Tool implementations (web search, code exec, etc.)
│   ├── agents/               # Individual agent implementations
│   │   ├── data_analyst.py   # Data analysis specialist (with tool integration)
│   │   ├── researcher.py     # Research and information gathering
│   │   └── code_generator.py # Code generation and engineering
│   └── __init__.py
├── tests/                     # Comprehensive unit tests
├── examples/                  # Usage examples (5 demos)
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── chroma_db/                # Vector database storage (created automatically)
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

# Optional: Tool API keys
SERPAPI_API_KEY=your_serpapi_key          # For web search
# Other tool configurations as needed
```
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

## � Tool Integration

Agents can use external tools to perform actions beyond text generation:

### Available Tools

- **Web Search**: Query external APIs for real-time information
- **Code Execution**: Run Python/bash scripts with security controls
- **Database Queries**: Execute SQL on SQLite databases
- **File System**: Safe file operations with path restrictions
- **API Calls**: Make HTTP requests to external services

### Tool Usage

```python
from src.tool_registry import get_tool_registry

# Get tool registry
registry = get_tool_registry()

# List available tools
tools = registry.get_available_tools()
print(f"Available tools: {[t.name for t in tools]}")

# Use code execution tool
code_tool = registry.get_tool("code_execution")
result = code_tool.execute("print('Hello from tool!')", "python")
print(f"Output: {result.data['output']}")

# Use database tool
db_tool = registry.get_tool("database_query")
result = db_tool.execute("SELECT sqlite_version()", "SELECT")
print(f"Version: {result.data['rows'][0][0]}")
```

### Agent Tool Integration

Agents automatically select and use appropriate tools:

```python
from src.orchestrator import Orchestrator

orchestrator = Orchestrator()

# Task automatically uses code execution for calculations
result = orchestrator.process_task(
    "Calculate the sum of numbers from 1 to 100 using Python"
)

# Check if tools were used
for agent in result['spawned_agents']:
    if 'tools_used' in agent:
        print(f"Agent {agent['agent_id']} used tools: {agent['tools_used']}")
```

### Custom Tool Creation

Create new tools by extending `BaseTool`:

```python
from src.tool_registry import BaseTool, ToolConfig, ToolResult
from src.tool_registry import ToolType

class CustomTool(BaseTool):
    def __init__(self, config: ToolConfig):
        super().__init__(config)
    
    def execute(self, **kwargs) -> ToolResult:
        # Implement tool logic
        return ToolResult(True, data={"result": "custom output"})

# Register tool
from src.tool_registry import get_tool_registry

config = ToolConfig(
    name="custom_tool",
    tool_type=ToolType.CUSTOM,
    description="My custom tool",
    parameters={},
    required_env_vars=[]
)

registry = get_tool_registry()
registry.register_config(config, CustomTool)
```

## �📊 State Management

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

### Example 4: Tool Integration
```bash
python examples/example4_tool_integration.py
```
Shows agents using external tools for enhanced capabilities.

### Example 5: Memory Integration
```bash
python examples/example5_memory_integration.py
```
Demonstrates persistent memory and conversation continuity across sessions.

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
