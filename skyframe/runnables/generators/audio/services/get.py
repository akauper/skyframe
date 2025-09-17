from typing import TypeVar

from .base import BaseAudioGenerationService

TAudioGenerationService = TypeVar("TAudioGenerationService", bound=BaseAudioGenerationService)


def get_audio_generation_service(service_name: str) -> TAudioGenerationService:
    if service_name == 'eleven_labs':
        from .eleven_labs import ElevenLabsGenerationService
        return ElevenLabsGenerationService()
    raise NotImplementedError(f'Audio Generation service: {service_name} is not implemented')