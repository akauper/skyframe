from typing import TypeVar

from .base import BaseModerationService

TModerationService = TypeVar("TModerationService", bound=BaseModerationService)


def get_moderation_service(service_name: str) -> TModerationService:
    if service_name == 'openai':
        from .openai import OpenaiModerationService
        return OpenaiModerationService()
    elif service_name == 'transformers':
        from .transformers import TransformersModerationService
        return TransformersModerationService()
    
    raise NotImplementedError(f'Moderation service: {service_name} is not implemented')