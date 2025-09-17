from typing import TypeVar, AsyncGenerator, ClassVar
from uuid import UUID

from skyframe.exceptions import GenerationException
from skyframe.runnables.models import RunContext
from .models import SpeechToTextGenerationParams, SpeechToTextRequest, SpeechToTextResponse, \
    SpeechToTextResponseChunk
from .services import BaseSpeechToTextGenerationService, get_speech_to_text_generation_service
from ..base import BaseGenerator

TGenerationService = TypeVar("TGenerationService", bound=BaseSpeechToTextGenerationService)


class SpeechToTextGenerator(BaseGenerator[SpeechToTextGenerationParams]):
    # service_name: str = Field(default=_DEFAULT_SERVICE_NAME)
    # generation_params: SpeechToTextGenerationParams = Field(default_factory=SpeechToTextGenerationParams)

    generator_name: ClassVar[str] = 'speech_to_text'

    def cleanup(self):
        del self.generation_params
        super().cleanup()

    def _get_generation_service(self) -> TGenerationService:
        try:
            return get_speech_to_text_generation_service(self.service_name)
        except NotImplementedError as e:
            raise GenerationException(
                message=f'Generation service {self.service_name} is not implemented',
                inner_exception=e
            )

    async def run_async(
            self,
            request: SpeechToTextRequest,
    ) -> SpeechToTextResponse:
        content = self._begin_run(generation_params=self.generation_params)
        generation_service = self._get_generation_service()

        await self._invoke_callback_async('on_speech_to_text_generation_start', request=request, **content)

        try:
            response = await generation_service.run_async(
                request=request,
                generation_params=self.generation_params
            )
        except Exception as e:
            await self._invoke_callback_async('on_speech_to_text_generation_error', error=e, **content)
            raise GenerationException(
                message=f'Error while generating speech to text: {e}',
                inner_exception=e
            )

        await self._invoke_callback_async('on_speech_to_text_generation_end', response=response, **content)

        return response

    # TODO: Add support for streaming
    def run_stream(
            self,
            request: SpeechToTextRequest,
    ) -> AsyncGenerator[SpeechToTextResponseChunk, None]:
        raise NotImplementedError()

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
