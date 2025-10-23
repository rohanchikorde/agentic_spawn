# AgentSpawn Setup Guide

## Prerequisites

- Python 3.9+
- OpenAI API key
- pip package manager

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `langgraph`: Graph-based workflow orchestration
- `langchain`: LLM framework and utilities
- `langchain-openai`: OpenAI integration
- `langchain-core`: Core LLM utilities
- `pydantic`: Data validation and settings management
- `python-dotenv`: Environment variable management

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-key-here
ORCHESTRATOR_MODEL=gpt-4
ORCHESTRATOR_TEMPERATURE=0.7
```

### 3. Verify Installation

Run the getting started demo:

```bash
python examples/getting_started.py
```

This should display demonstrations of all core features without requiring API calls.

### 4. Run Unit Tests

Verify everything is working correctly:

```bash
python -m pytest tests/ -v
```

Expected output: All 25+ tests should pass ✓

## Project Structure Overview

```
agentic_spawn/
├── src/                    # Core framework
│   ├── orchestrator.py     # Main orchestration engine
│   ├── agent_registry.py   # Agent management system
│   ├── state.py           # State management structures
│   ├── utils.py           # Utility functions
│   └── agents/            # Specialized agents
├── tests/                  # Unit tests
├── examples/               # Usage examples
├── requirements.txt        # Dependencies
└── README.md              # Full documentation
```

## Quick Start

### Basic Usage

```python
from src.orchestrator import Orchestrator

orchestrator = Orchestrator(model_name="gpt-4")
result = orchestrator.process_task("Your task here")

print(result['final_response'])
```

### Run Examples

```bash
# Interactive demo of all concepts
python examples/getting_started.py

# Simple task processing
python examples/example1_simple_task.py

# Complex multi-agent orchestration
python examples/example2_complex_task.py

# Direct agent usage
python examples/example3_direct_agents.py
```

## Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Required | Your OpenAI API key |
| `ORCHESTRATOR_MODEL` | gpt-4 | LLM model for orchestrator |
| `ORCHESTRATOR_TEMPERATURE` | 0.7 | Randomness (0-1) |
| `AGENT_TEMPERATURE` | 0.5 | Agent randomness (0-1) |
| `MAX_RETRIES` | 3 | Retry attempts |
| `AGENT_TIMEOUT` | 30 | Timeout in seconds |

### Code Configuration

In `src/orchestrator.py`:
```python
orchestrator = Orchestrator(
    model_name="gpt-4",           # Change LLM model
    temperature=0.7               # Adjust randomness
)
```

## Architecture Overview

### The Orchestration Workflow

1. **Assess Complexity** → Analyze keywords and patterns
2. **Decide Agents** → Determine which agents to spawn
3. **Spawn Agents** → Create and execute specialized agents
4. **Aggregate Results** → Synthesize into final response

### Complexity Levels

- **SIMPLE**: Direct reasoning (no agents)
- **MODERATE**: Spawn detected specialists
- **COMPLEX**: Spawn all available specialists

### Agent Types

- **Data Analyst**: Statistical analysis and metrics
- **Researcher**: Information gathering and investigation
- **Code Generator**: Code generation and implementation

## Testing

### Run All Tests
```bash
python -m pytest tests/
```

### Run Specific Test
```bash
python -m pytest tests/test_framework.py::TestUtils::test_assess_task_complexity_simple
```

### Run with Coverage
```bash
python -m pytest tests/ --cov=src
```

## Customization

### Add Custom Keywords

Edit `src/utils.py`:
```python
COMPLEXITY_KEYWORDS[ComplexityLevel.SIMPLE].extend(["your_keyword"])
AGENT_KEYWORDS["data_analyst"].extend(["your_keyword"])
```

### Register Custom Agent

```python
from src.agent_registry import get_registry, AgentConfig
from src.state import AgentType

registry = get_registry()
config = AgentConfig(
    agent_type=AgentType.GENERAL,
    name="Custom Agent",
    description="Your description",
    system_prompt="Your system prompt",
    capabilities=["capability1", "capability2"]
)
registry.register_agent(config)
```

## Troubleshooting

### "OpenAI API key not found"
- Verify `.env` file exists in project root
- Check that `OPENAI_API_KEY` is set correctly
- Ensure no extra spaces in the key

### "Module not found" errors
- Verify all files in `src/` directory
- Check Python path includes project root
- Try: `python -m pytest tests/` from project root

### Tests failing
- Run `python -m pytest tests/ -v` for detailed output
- Check that all dependencies are installed
- Verify Python version is 3.9+

### LLM calls failing
- Verify API key is valid and has credits
- Check internet connection
- Try with a simpler task first

## Performance Optimization

1. **Use Simple Tasks When Possible**
   - No agent spawning = faster and cheaper
   - Direct LLM reasoning is sufficient for many tasks

2. **Adjust Temperature**
   - Lower (0.3-0.5) for analysis and code
   - Higher (0.7-0.9) for creative tasks

3. **Batch Processing**
   - Group similar tasks together
   - Cache results when possible

4. **Monitor Usage**
   - Check `result['spawned_agents']` to see agent usage
   - Track API costs by analyzing spawned agents

## Development Workflow

1. **Make Changes**
   - Edit files in `src/`
   - Write tests in `tests/`

2. **Test Changes**
   ```bash
   python -m pytest tests/ -v
   ```

3. **Check Examples**
   ```bash
   python examples/getting_started.py
   ```

4. **Review Code**
   - Follow existing patterns
   - Add docstrings
   - Include type hints

## Next Steps

1. Review [README.md](README.md) for detailed documentation
2. Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for code snippets
3. Explore [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for architecture details
4. Run examples to understand usage patterns
5. Read test cases for implementation examples

## Support

- Review documentation in `README.md`
- Check examples in `examples/` directory
- Look at test cases in `tests/` for usage patterns
- Check `QUICK_REFERENCE.md` for common issues

## Resources

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [LangChain Documentation](https://www.langchain.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

---

**Setup complete!** 🚀 Run `python examples/getting_started.py` to start using AgentSpawn.
