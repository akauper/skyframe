from typing import List, Optional, Iterator

from pydantic import BaseModel, Field

from .base import UIDMixin, CreatedAtMixin, UpdatedAtMixin
from .message import Message, MessageRole


class ConversationMixin(BaseModel):
    messages: List[Message] = Field(default_factory=list)

    def __len__(self) -> int:
        """Return the number of messages in the conversation."""
        return len(self.messages)

    def __iter__(self) -> Iterator[Message]:
        """Return an iterator for the conversation's messages."""
        return iter(self.messages)

    def __getitem__(self, index: int) -> Message:
        """Return the message at the specified index."""
        return self.messages[index]

    def __setitem__(self, index: int, message: Message) -> None:
        """Set the message at the specified index."""
        self.add_message(message, index=index)

    def __iadd__(self, message: Message) -> None:
        """Add a message to the end of the conversation."""
        self.add_message(message)

    @property
    def last_message(self) -> Optional[Message]:
        return self.messages[-1] if self.messages and len(self.messages) > 0 else None

    @property
    def system_message(self) -> Optional[Message]:
        if not self.messages or len(self.messages) == 0:
            return None
        if self.messages[0].is_from(MessageRole.system):
            return self.messages[0]
        return None

    def to_string(self, omit_system_messages: bool = False) -> str:
        string = Message.join_as_string(self.messages, omit_system_messages)
        return string

    def add_message(self, message: Message, index: int = -1) -> None:
        if index == -1:
            self.messages.append(message)
        else:
            self.messages.insert(index, message)

    def pop(self, index: Optional[int] = None) -> Message:
        if index is None:
            return self.messages.pop()
        else:
            return self.messages.pop(index)

    def clear(self) -> None:
        self.messages = []


class Conversation(UIDMixin, CreatedAtMixin, UpdatedAtMixin, ConversationMixin):

    @staticmethod
    def join_as_string(conversations: List['Conversation'], omit_system_messages: bool = False) -> str:
        conversations_str = ''
        for conversation in conversations:
            conversations_str += f'{conversation.to_string(omit_system_messages)}\n\n'
        return conversations_str

    def prune_system_messages(self) -> 'Conversation':
        new_messages = [m for m in self.messages if not m.is_from(MessageRole.system)]
        return self.__class__(messages=new_messages)
