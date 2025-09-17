from typing import Optional, AsyncIterator, Callable

from pydantic import Field

from skyframe.models.base import BaseParams


class AudioGenerationParams(BaseParams):
    """
    Parameters for generating audio from an STT Service.
    """

    voice_id: Optional[str] = Field(default="EXAVITQu4vr4xnSDxMaL")
    """ The voice ID to use for the generation. """

    model: str = Field(default="eleven_turbo_v2")
    """ The model ID to use for the generation. """

    stability: Optional[float] = Field(default=0.71, ge=0.0, le=1.0)
    """ The stability of the voice. """

    similarity_boost: Optional[float] = Field(default=0.5, ge=0.0, le=1.0)
    """ The similarity boost of the voice. """

    style: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)
    """ The style of the voice. """

    use_speaker_boost: Optional[bool] = Field(default=True)
    """ Whether to use speaker boost. """

    output_format: Optional[str] = Field(default="mp3_44100_128")
    """ The output format of the audio. """

    latency: Optional[int] = Field(default=1)
    """ The latency of the audio. """

    stream_chunk_size: Optional[int] = Field(default=2048)
    """ The stream chunk size of the audio. """

    text_chunker: Optional[Callable[[AsyncIterator[str]], AsyncIterator[str]]] = Field(default=None)
    """ An method that takes an AsyncIterator and returns an AsyncIterator to chunk the text. """
