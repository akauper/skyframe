import asyncio
from typing import Optional, List, Callable, Any, Generator

from pydantic import Field

from skyframe.utils import logger

from ..memory import ConversationMemory
from ...generators.text import TextGenerator
from ...generators.text.models import TextGenerationRequest
from skyframe.prompting.models import Prompt
from skyframe.models import Message, MessageRole

_DEFAULT_SUMMARY_TEMPLATE = """Progressively summarize the lines of conversation provided, adding onto the previous summary returning a new summary.

EXAMPLE
Current summary:
The human asks what the AI thinks of artificial intelligence. The AI thinks artificial intelligence is a force for good.

New lines of conversation:
Human: Why do you think artificial intelligence is a force for good?
AI: Because artificial intelligence will help humans reach their full potential.

New summary:
The human asks what the AI thinks of artificial intelligence. The AI thinks artificial intelligence is a force for good because it will help humans reach their full potential.
END OF EXAMPLE

Current summary:
{summary}

New lines of conversation:
{new_lines}

New summary:"""

_DEFAULT_MAX_BUFFER_TOKENS = 2100
_DEFAULT_SUMMARIZE_MESSAGE_BATCH = 4


class ConversationSummaryMemory(ConversationMemory):
    summary_generator: TextGenerator = Field(default_factory=TextGenerator)
    max_buffer_tokens: int = Field(default=_DEFAULT_MAX_BUFFER_TOKENS)

    summarize_prompt: Prompt = Field(default_factory=lambda: Prompt(template=_DEFAULT_SUMMARY_TEMPLATE))
    moving_summary_buffer: str = Field(default="")
    summarize_message_batch: int = Field(default=_DEFAULT_SUMMARIZE_MESSAGE_BATCH)

    def cleanup(self):
        self.summary_generator.cleanup()
        del self.summary_generator
        super().cleanup()

    def save(self, request: TextGenerationRequest) -> None:
        super().save(request)
        self.prune()

    def __pretty__(self, fmt: Callable[[Any], Any], **kwargs: Any) -> Generator[Any, None, None]:
        yield self.__class__.__name__
        yield 1
        yield f'Max Buffer Tokens: {self.max_buffer_tokens}'
        yield 0
        yield f'Summarize Message Batch: {self.summarize_message_batch}'
        yield 0
        yield f'Moving Summary Buffer: {self.moving_summary_buffer}'
        yield 0
        yield f'Messages:'
        yield fmt(self.messages)

    def predict_new_summary(self, messages: List[Message], existing_summary: str) -> str:
        new_lines = Message.join_as_string(messages)
        _input = self.summarize_prompt.format(summary=existing_summary, new_lines=new_lines)

        event_loop = asyncio.get_event_loop()

        future = asyncio.run_coroutine_threadsafe(self.summary_generator.run_async(_input), event_loop)
        completion = future.result()

        new_summary = completion.choice.content.strip()
        return new_summary

    def get_token_count(self) -> int:
        return self.summary_generator.get_token_count(self.messages)

    def prune(self) -> None:
        def pop_first_message() -> Optional[Message]:
            for index, message in enumerate(self):
                if not message.is_from(MessageRole.system) and not message.is_from(MessageRole.summary):
                    return self.pop(index)
            return None

        def popable_length() -> int:
            length = 0
            for message in self:
                if not message.is_from(MessageRole.system) and not message.is_from(MessageRole.summary):
                    length += 1
            return length

        if len(self) == 0 or popable_length() == 0:
            return

        buffer_tokens: int = self.get_token_count()
        if buffer_tokens > self.max_buffer_tokens:
            pruned_messages = []
            start_buffer_tokens: int = buffer_tokens

            error = False
            while not error and buffer_tokens > self.max_buffer_tokens:
                batch = min(self.summarize_message_batch, popable_length())
                for i in range(batch):
                    popped = pop_first_message()
                    if popped is not None:
                        pruned_messages.append(popped)
                    else:
                        error = True
                        break
                buffer_tokens = self.get_token_count()

            self.moving_summary_buffer = self.predict_new_summary(pruned_messages, self.moving_summary_buffer)
            insert_index = 1 if self[0].is_from(MessageRole.system) else 0
            self.insert(insert_index, Message.from_summary(self.moving_summary_buffer))
            buffer_tokens = self.get_token_count()
            logger.info(f'Pruned {len(pruned_messages)} messages from memory. New Token Count: {buffer_tokens} Old Token Count: {start_buffer_tokens} New summary: {self.moving_summary_buffer}')

    def clear(self) -> None:
        super().clear()
        self.moving_summary_buffer = ""
