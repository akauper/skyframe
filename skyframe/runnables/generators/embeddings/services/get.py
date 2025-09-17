from typing import TypeVar
from .base import BaseEmbeddingsGenerationService

TEmbeddingsGenerationService = TypeVar("TEmbeddingsGenerationService", bound=BaseEmbeddingsGenerationService)


def get_embeddings_generation_service(service_name: str) -> TEmbeddingsGenerationService:
    if service_name == 'openai':
        from .openai import OpenAiEmbeddingsGenerationService
        return OpenAiEmbeddingsGenerationService()

    raise NotImplementedError(f'Embedding Generation service: {service_name} is not implemented')