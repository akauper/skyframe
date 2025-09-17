from typing import List, Callable, Any, Generator

from skyframe.models.conversation import ConversationMixin
from skyframe.models.message import Message
from ...generators.text.models import TextGenerationRequest


class ConversationMemory(ConversationMixin):

    def cleanup(self):
        self.clear()

    def load(self) -> List[Message]:
        return self.messages

    def save(self, request: TextGenerationRequest) -> None:
        if isinstance(request, list):
            for msg in request:
                self.add_message(msg)
        elif isinstance(request, Message):
            self.add_message(request)
        elif isinstance(request, str):
            self.add_message(Message.from_user(request))
        else:
            raise TypeError(f'Expected GenerationRequest or List[Message], got {type(request)}')

    def __pretty__(self, fmt: Callable[[Any], Any], **kwargs: Any) -> Generator[Any, None, None]:
        yield 'ConversationMemory'
        yield 1
        yield f'Messages:'
        yield fmt(self.messages)