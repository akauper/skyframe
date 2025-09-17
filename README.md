# SkyFramework

A lightweight, personal LLM orchestration framework for building AI-powered applications with unified interfaces across multiple providers.

## Features

- **Multi-Provider Support**: OpenAI, Anthropic, ElevenLabs, Transformers
- **Async Architecture**: Built for performance with async/await throughout
- **Pipeline System**: Chain multiple operations with automatic error handling
- **Agent Framework**: Memory-enabled agents with tool usage capabilities
- **Evaluation Suite**: Model-graded assertions and comprehensive testing tools
- **Type Safety**: Full type hints with Pydantic v2 models

## Quick Start

```python
# Basic imports and data models
from skyframe import (
    TextGenerator, Pipeline, Runnable,
    Message, Conversation, Prompt
)
from skyframe.runnables.generators.text.models import TextGenerationParams

# The framework uses a modular architecture with data models
message = Message.from_user("Hello, world!")
conversation = Conversation()
conversation.add_message(message)

# Generation parameters are strongly typed
params = TextGenerationParams(
    model="gpt-4",
    temperature=0.7,
    max_tokens=100
)

# Generators require configuration setup for actual API calls
# See installation section for environment setup
```

## Architecture Overview

SkyFramework uses a declarative approach with strongly-typed components:

```python
# All components inherit from Runnable base class
class MyProcessor(Runnable):
    async def run_async(self, input_data):
        # Process data
        return result

# Pipeline multiple operations
pipeline = Pipeline([
    MyProcessor(),
    AnotherProcessor()
])

# Async execution throughout
result = await pipeline.run_async(input_data)
```

## Architecture

- **Runnables**: Base abstraction for all components
- **Generators**: Service integrations (text, audio, embeddings, moderation)
- **Agents**: Advanced components with memory and tool access
- **Evaluation**: Framework for testing and validating LLM outputs

## Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd skyframe

# Install dependencies
uv sync
```

## Setup

1. **Environment Variables**: Copy the example environment file and add your API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys for desired providers
   ```

2. **Try the Example**: Run the basic example to see the framework in action:
   ```bash
   uv run python example.py
   ```

3. **Configuration**: For production use, configure the framework settings according to your needs.

## Requirements

- Python ≥3.12
- API keys for desired providers (OpenAI, Anthropic, etc.)

---

*Built with modern Python practices: async/await, Pydantic v2, comprehensive type hints*