from typing import Any, List, TypeVar, Optional, ClassVar
from uuid import UUID

from skyframe.exceptions.generation import GenerationException
from skyframe.runnables.models.run_info import RunContext
from .models import EmbeddingsGenerationParams, EmbeddingsResponse, EmbeddingsGenerationRequest
from .services import BaseEmbeddingsGenerationService, get_embeddings_generation_service
from ..base import BaseGenerator

TGenerationService = TypeVar("TGenerationService", bound=BaseEmbeddingsGenerationService)


class EmbeddingsGenerator(BaseGenerator[EmbeddingsGenerationParams]):
    # service_name: str = Field(default=_DEFAULT_SERVICE_NAME)
    # generation_params: EmbeddingsGenerationParams = Field(default_factory=EmbeddingsGenerationParams)

    generator_name: ClassVar[str] = 'embeddings'

    def cleanup(self):
        del self.generation_params
        super().cleanup()

    def try_set(self, **data: Any) -> List[str]:
        used = super().try_set(**data)
        if 'service_name' in data:
            self.service_name = data['service_name']
            used.append('service_name')
        used += self.generation_params.try_set(**data)
        return used

    def _get_generation_service(self) -> TGenerationService:
        try:
            return get_embeddings_generation_service(self.service_name)
        except NotImplementedError as e:
            raise GenerationException(
                message=f'Embedding Generation service {self.service_name} is not implemented',
                inner_exception=e
            )

    def run(
            self,
            request: EmbeddingsGenerationRequest,
            override_params: Optional[EmbeddingsGenerationParams] = None
    ) -> EmbeddingsResponse:
        generation_params = self.generation_params.merge(override_params)

        context = self._begin_run(generation_params=generation_params)
        generation_service = self._get_generation_service()

        self._invoke_callback('on_embeddings_generation_start', request=request, **context)

        try:
            response = generation_service.run(
                request=request,
                generation_params=generation_params
            )
        except Exception as e:
            self._invoke_callback('on_embeddings_generation_error', exception=e, **context)
            raise GenerationException(
                message='Error while generating embeddings',
                inner_exception=e
            )

        self._invoke_callback('on_embeddings_generation_end', response=response, **context)

        return response

    async def run_async(
            self,
            request: EmbeddingsGenerationRequest,
            override_params: Optional[EmbeddingsGenerationParams] = None
    ) -> EmbeddingsResponse:
        generation_params = self.generation_params.merge(override_params)

        context = self._begin_run(generation_params=generation_params)
        generation_service = self._get_generation_service()

        self._invoke_callback('on_embeddings_generation_start', request=request, **context)

        try:
            response = await generation_service.run_async(
                request=request,
                generation_params=generation_params
            )
        except Exception as e:
            self._invoke_callback('on_embeddings_generation_error', exception=e, **context)
            raise GenerationException(
                message='Error while generating embeddings',
                inner_exception=e
            )

        self._invoke_callback('on_embeddings_generation_end', response=response, **context)

        return response

    def _begin_run(
            self,
            *,
            run_id: UUID = None,
            parent_run_id: UUID = None,
            **kwargs
    ) -> RunContext:
        return super()._begin_run(
            run_id=run_id,
            parent_run_id=parent_run_id,
            generator=self,
            **kwargs
        )
