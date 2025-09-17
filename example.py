#!/usr/bin/env python3
"""
SkyFramework Basic Example

This example demonstrates the core concepts and data models of SkyFramework
without requiring API keys or external services.
"""

import asyncio
from skyframe import (
    Message, MessageRole, Conversation,
    Prompt, Pipeline, Runnable
)
from skyframe.runnables.generators.text.models import TextGenerationParams


class MockProcessor(Runnable):
    """Example custom processor that demonstrates the Runnable interface."""

    async def run_async(self, **kwargs) -> dict:
        """Process input data and return modified result."""
        # Extract input data
        input_text = kwargs.get('input', 'default')
        processed = f"Processed: {input_text.upper()}"
        return {'input': processed}


async def main():
    """Demonstrate SkyFramework's core functionality."""

    print("SkyFramework Example")
    print("=" * 40)

    # 1. Working with Messages
    print("\n1. Creating Messages:")

    user_msg = Message.from_user("Hello, how are you?")
    ai_msg = Message.from_ai("I'm doing well, thank you!")
    system_msg = Message.from_system("You are a helpful assistant.")

    print(f"User: {user_msg.content}")
    print(f"AI: {ai_msg.content}")
    print(f"System: {system_msg.content}")

    # 2. Working with Conversations
    print("\n2. Building Conversations:")

    conversation = Conversation()
    conversation.add_message(system_msg)
    conversation.add_message(user_msg)
    conversation.add_message(ai_msg)

    print(f"Conversation has {len(conversation.messages)} messages")
    for i, msg in enumerate(conversation.messages):
        print(f"  {i+1}. [{msg.role}] {msg.content[:30]}...")

    # 3. Working with Prompts
    print("\n3. Template Processing:")

    template = "Hello {name}, welcome to {platform}!"
    prompt = Prompt(template=template)

    rendered = prompt.format(name="Alice", platform="SkyFramework")
    print(f"Template: {template}")
    print(f"Rendered: {rendered}")

    # 4. Working with Generation Parameters
    print("\n4. Generation Parameters:")

    params = TextGenerationParams(
        model="gpt-4",
        temperature=0.7,
        max_tokens=100,
        stop=["END"]
    )

    print(f"Model: {params.model}")
    print(f"Temperature: {params.temperature}")
    print(f"Max Tokens: {params.max_tokens}")
    print(f"Stop Sequences: {params.stop}")

    # 5. Working with Pipelines
    print("\n5. Pipeline Processing:")

    # Create a simple pipeline with custom processors
    pipeline = Pipeline(runnables=[
        MockProcessor(),
        MockProcessor()  # Will process twice
    ])

    input_text = "hello world"
    result = await pipeline.run_async(input=input_text)
    print(f"Input: {input_text}")
    print(f"Pipeline Result: {result}")

    # 6. Demonstrate Type Safety
    print("\n6. Type Safety:")

    try:
        # This would catch type errors at runtime with Pydantic validation
        params_with_validation = TextGenerationParams(
            model="gpt-4",
            temperature=0.8,  # Valid: 0-2
            max_tokens=50
        )
        print(f"SUCCESS: Valid parameters: {params_with_validation.model}")
    except Exception as e:
        print(f"ERROR: Validation error: {e}")

    print("\nExample completed!")
    print("\nNext steps:")
    print("- Set up API keys in .env file (see .env.example)")
    print("- Configure framework settings for actual LLM calls")
    print("- Explore the evaluation and agent capabilities")


if __name__ == "__main__":
    asyncio.run(main())