from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from .role import MessageRole

if TYPE_CHECKING:
    from .base import Message


class MessageChunk(BaseModel):
    index: int
    """ The index of this chunk in the stream. """

    message_id: str
    """ The uid of the message this chunk is part of. """

    role: MessageRole
    """ The role of the message this chunk is part of. """

    content: str
    """ The content of this chunk. """

    is_final: bool = Field(default=False)
    """ Whether this chunk is the final chunk of the message. """

    @classmethod
    def of_message(
            cls,
            index: int,
            message: 'Message',
            content: str,
            is_final: bool = False,
    ) -> 'MessageChunk':
        return cls(
            index=index,
            message_id=message.id,
            role=message.role,
            content=content,
            is_final=is_final,
        )