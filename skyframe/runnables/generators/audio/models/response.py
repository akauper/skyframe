from typing import Optional, List

from pydantic import BaseModel, Field

from skyframe.models.base import UIDMixin, CreatedAtMixin


class NormalizedAlignment(BaseModel):
    char_start_times_ms: List[int] = Field(default=[])
    """A list of starting times (in milliseconds) for each character in the normalized text as it corresponds to the audio. For instance, the character ‘H’ starts at time 0 ms in the audio."""

    chars_durations_ms: List[int] = Field(default=[])
    """A list providing the duration (in milliseconds) for each character’s pronunciation in the audio. For instance, the character ‘H’ has a pronunciation duration of 3 ms."""

    chars: List[str] = Field(default=[])
    """The list of characters in the normalized text sequence that corresponds with the timings and durations. This list is used to map the characters to their respective starting times and durations."""


class AudioResponseChunk(BaseModel):
    """
    Represents an audio response chunk from a text-to-speech model.
    The message content is encoded as a base64 string.

    This class is used is what Quiply converts all audio response chunks from different services into.
    """

    index: int
    """The index of this audio response chunk in the sequence of audio response chunks."""

    audio: Optional[str] = Field(default=None)
    """The generated audio chunk encoded as a base64 string."""

    normalized_alignment: Optional[NormalizedAlignment] = Field(default=None)
    """Alignment information for the generated audio given the input normalized text sequence."""

    is_start: bool = Field(default=False)
    """Whether this audio response is the start of a streaming response."""

    is_final: bool = Field(default=False)
    """Whether this chunk is the final chunk in a streaming response."""


class AudioResponse(UIDMixin, CreatedAtMixin):
    """
    Represents an audio response from a text-to-speech model.
    The message content is encoded as a base64 string.

    This class is used is what Quiply converts all audio responses from different services into.
    """

    audio: Optional[str] = Field(default=None)
    """The generated audio encoded as a base64 string."""

    normalized_alignment: Optional[NormalizedAlignment] = Field(default=None)
    """Alignment information for the generated audio given the input normalized text sequence."""

    @classmethod
    def from_chunks(
            cls,
            chunks: List[AudioResponseChunk]
    ) -> 'AudioResponse':
        """
        Combine a list of audio response chunks into a single audio response.
        """

        if not chunks or len(chunks) == 0:
            raise ValueError("Cannot create an AudioResponse from an empty list of chunks.")

        audio = ''
        normalized_alignment = chunks[0].normalized_alignment or None

        for chunk in chunks:
            if chunk.audio:
                audio += chunk.audio

        return cls(
            audio=audio,
            normalized_alignment=normalized_alignment,
        )