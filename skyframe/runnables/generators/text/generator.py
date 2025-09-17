import time
from typing import TypeVar, AsyncGenerator, List, Any, Optional, ClassVar
from uuid import UUID

from skyframe.exceptions.generation import GenerationException
from skyframe.runnables.models import RunContext
from skyframe.utils import logger
from .models import TextGenerationParams, TextGenerationRequest, TextResponse, TextResponseChunk
from .services import BaseTextGenerationService, get_text_generation_service
from ..base import BaseGenerator

TGenerationService = TypeVar("TGenerationService", bound=BaseTextGenerationService)


# @evaluate
class TextGenerator(BaseGenerator[TextGenerationParams]):
    # service_name: str = Field(default=_DEFAULT_SERVICE_NAME)
    # generation_params: TextGenerationParams = Field(default_factory=TextGenerationParams)

    generator_name: ClassVar[str] = 'text'

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
            return get_text_generation_service(self.service_name)
        except NotImplementedError as e:
            raise GenerationException(
                message=f'Text Generation service {self.service_name} is not implemented',
                inner_exception=e
            )

    def run(
            self,
            request: TextGenerationRequest,
            override_params: Optional[TextGenerationParams] = None
    ) -> TextResponse:
        generation_params = self.generation_params.merge(override_params)

        context = self._begin_run(generation_params=generation_params)
        generation_service = self._get_generation_service()

        self._invoke_callback('on_text_generation_start', request=request, **context)

        try:
            response = generation_service.run(
                request=request,
                generation_params=generation_params
            )
        except Exception as e:
            self._invoke_callback('on_text_generation_error', error=e, **context)
            raise GenerationException(
                message=f'Error while generating text: {e}',
                inner_exception=e
            )

        self._invoke_callback('on_text_generation_end', response=response, **context)

        return response

    # @evaluate_async('_eval_run')
    async def run_async(
            self,
            request: TextGenerationRequest,
            *,
            override_params: Optional[TextGenerationParams] = None,
            run_id: Optional[UUID] = None,
    ) -> TextResponse:
        generation_params = self.generation_params.merge(override_params)

        context = self._begin_run(run_id=run_id, generation_params=generation_params)
        generation_service = self._get_generation_service()

        await self._invoke_callback_async('on_text_generation_start', request=request, **context)

        try:
            # service_call = ServiceCall(service_name=self.service_name, service_type='text_generation')
            response: TextResponse = await generation_service.run_async(
                request=request,
                generation_params=generation_params
            )
            # service_call.end(response=response)
        except Exception as e:
            await self._invoke_callback_async('on_text_generation_error', error=e, **context)
            raise GenerationException(
                message=f'Error while generating text: {e}',
                inner_exception=e
            )

        await self._invoke_callback_async('on_text_generation_end', response=response, **context)

        return response

    async def run_stream(
            self,
            request: TextGenerationRequest,
            *,
            override_params: Optional[TextGenerationParams] = None,
            run_id: Optional[UUID] = None,
    ) -> AsyncGenerator[TextResponseChunk, None]:
        generation_params = self.generation_params.merge(override_params)

        context = self._begin_run(run_id=run_id, generation_params=generation_params)
        generation_service = self._get_generation_service()

        await self._invoke_callback_async('on_text_generation_start', request=request, **context)

        start_time = time.time()

        try:
            generator = await generation_service.run_stream(
                request=request,
                generation_params=generation_params
            )
        except Exception as e:
            await self._invoke_callback_async('on_text_generation_error', error=e, **context)
            raise GenerationException(
                message=f'Error while generating text: {e}',
                inner_exception=e
            )

        chunks: List[TextResponseChunk] = []

        async for chunk in generator:
            chunks.append(chunk)
            await self._invoke_callback_async('on_text_generation_chunk', chunk=chunk, **context)
            yield chunk

        response = TextResponse.from_chunks(chunks)
        logger.info(f'Called TextGeneration service {self.service_name} in {round(time.time() - start_time, 2)} seconds. Usage {response.token_usage}')

        await self._invoke_callback_async('on_text_generation_end', response=response, **context)

    def get_token_count(
            self,
            request: TextGenerationRequest
    ) -> int:
        generation_service = self._get_generation_service()

        return generation_service.get_token_count(
            request=request,
            generation_info=self.generation_params
        )

    async def _eval_run(self, *args, **kwargs):
        logger.error('eval run kwargs', kwargs)
        request: TextGenerationRequest = args[0]
        override_params: Optional[TextGenerationParams] = kwargs.get('override_params', None)
        generation_params = self.generation_params.merge(override_params)

        run_ctx = self._begin_run(parent_run_id=kwargs.get('run_id', None), generation_params=generation_params, eval_run=True)
        generation_service = self._get_generation_service()

        await self._invoke_callback_async('on_text_generation_start', request=request, **run_ctx)

        try:
            response = await generation_service.run_async(
                request=request,
                generation_params=generation_params
            )
        except Exception as e:
            await self._invoke_callback_async('on_text_generation_error', error=e, **run_ctx)
            raise GenerationException(
                message=f'Error while generating text: {e}',
                inner_exception=e
            )

        await self._invoke_callback_async('on_text_generation_end', response=response, **run_ctx)

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
