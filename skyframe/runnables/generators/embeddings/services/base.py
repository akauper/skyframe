from abc import ABC, abstractmethod
from typing import Any

from ..models import EmbeddingsGenerationRequest, EmbeddingsGenerationParams, EmbeddingsResponse


class BaseEmbeddingsGenerationService(ABC):
    @staticmethod
    @abstractmethod
    def calculate_cost(
            token_count: int,
            model_name: str,
    ) -> float:
        pass

    @abstractmethod
    def run(
            self,
            request: EmbeddingsGenerationRequest,
            generation_params: EmbeddingsGenerationParams
    ) -> Any:
        pass

    @abstractmethod
    async def run_async(
            self,
            request: EmbeddingsGenerationRequest,
            generation_params: EmbeddingsGenerationParams
    ) -> EmbeddingsResponse:
        pass
