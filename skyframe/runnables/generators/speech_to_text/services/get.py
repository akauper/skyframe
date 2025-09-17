from typing import TypeVar

from .base import BaseSpeechToTextGenerationService

TSpeechToTextGenerationService = TypeVar("TSpeechToTextGenerationService", bound=BaseSpeechToTextGenerationService)


def get_speech_to_text_generation_service(service_name: str) -> TSpeechToTextGenerationService:
    raise NotImplementedError(f'Speech to Text Generation service: {service_name} is not implemented')