from typing import TypeVar

from .base import BaseTextGenerationService

TTextGenerationService = TypeVar("TTextGenerationService", bound=BaseTextGenerationService)


def get_text_generation_service(service_name: str) -> TTextGenerationService:
    if service_name == 'openai':
        from .openai import OpenAiGenerationService
        return OpenAiGenerationService()
    elif service_name == 'anthropic':
        from .anthropic import AnthropicGenerationService
        return AnthropicGenerationService()
    else:
        raise NotImplementedError(f'Generation service: {service_name} is not implemented')
