from typing import Optional

from pydantic import Field, BaseModel

from skyframe.models.base import UIDMixin, CreatedAtMixin
from .response import AudioResponse, NormalizedAlignment


class MessageAudio(UIDMixin, CreatedAtMixin):
    """
    Audio that is generated from a Message.
    Remember Message always comes from an Agent or a User in a Conversation.

    MessageAudio differs from AudioResponse in specificity; it was ALWAYS generated from a Message.
    """

    message_id: str
    """ The uid of the Message this audio was generated from. """

    audio: Optional[str] = Field(default=None)
    """ The generated audio encoded as a base64 string. """

    normalized_alignment: Optional[NormalizedAlignment] = Field(default=None)
    """ Alignment information for the generated audio given the input normalized text sequence. """


class MessageAudioChunk(BaseModel):
    index: int
    """ The index of this chunk in the stream. """

    message_id: str
    """ The uid of the Message this audio chunk was generated from. """

    message_audio_id: str
    """ The uid of the MessageAudio this chunk is part of. """

    audio: Optional[str] = Field(default=None)
    """ The generated audio chunk encoded as a base64 string. """

    normalized_alignment: Optional[NormalizedAlignment] = Field(default=None)
    """ Alignment information for the generated audio given the input normalized text sequence. """

    is_final: bool = Field(default=False)
    """ Whether this chunk is the final chunk of the MessageAudio. """

    @classmethod
    def of_message_audio(
            cls,
            index: int,
            message_audio: MessageAudio,
            audio: str,
            normalized_alignment: Optional[AudioResponse] = None,
            is_final: bool = False,
    ) -> 'MessageAudioChunk':
        return cls(
            index=index,
            message_id=message_audio.message_id,
            message_audio_id=message_audio.id,
            audio=audio,
            normalized_alignment=normalized_alignment,
            is_final=is_final,
        )
