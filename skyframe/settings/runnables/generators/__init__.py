from pydantic import Field
from pydantic_settings import BaseSettings

from .audio import AudioSettings
from .diarization import DiarizationSettings
from .embeddings import EmbeddingSettings
from .moderation import ModerationSettings
from .speech_to_text import SpeechToTextSettings
from .text import TextSettings


class GeneratorSettings(BaseSettings):
    audio: AudioSettings = Field(default_factory=AudioSettings)
    diarization: DiarizationSettings = Field(default_factory=DiarizationSettings)
    embeddings: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    moderation: ModerationSettings = Field(default_factory=ModerationSettings)
    speech_to_text: SpeechToTextSettings = Field(default_factory=SpeechToTextSettings)
    text: TextSettings = Field(default_factory=TextSettings)

