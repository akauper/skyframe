from typing import List, TypeVar, ClassVar
from uuid import UUID

from pydantic import Field

from skyframe.runnables.models import RunContext
from skyframe.exceptions import GenerationException
from .models import ModerationGenerationParams, ModerationResponse
from .services import BaseModerationService, get_moderation_service
from ..base import BaseGenerator

TGenerationService = TypeVar("TGenerationService", bound=BaseModerationService)


class ModerationGenerator(BaseGenerator[ModerationGenerationParams]):
    service_names: List[str] = Field(default_factory=lambda: ['openai', 'transformers'])
    # service_names: List[str] = Field(default_factory=lambda: ['openai'])
    # generation_params: ModerationGenerationParams = Field(default_factory=ModerationGenerationParams)

    generator_name: ClassVar[str] = 'moderation'

    def cleanup(self):
        del self.generation_params
        super().cleanup()

    def _get_generation_services(self) -> List[TGenerationService]:
        try:
            return [get_moderation_service(service_name) for service_name in self.service_names]
        except NotImplementedError as e:
            raise GenerationException(
                message=f'Generation service {self.service_name} is not implemented',
                inner_exception=e
            )

    def run(
            self,
            request: str
    ) -> ModerationResponse:
        context = self._begin_run(generation_params=self.generation_params)

        self._invoke_callback('on_moderation_generation_start', request=request, **context)

        try:
            generation_services = self._get_generation_services()

            response = ModerationResponse(model='', flagged=False)
            for generation_service in generation_services:
                response += generation_service.run(request=request, generation_params=self.generation_params)
        except Exception as e:
            self._invoke_callback('on_moderation_generation_error', error=e, **context)
            raise GenerationException(
                message=f'Error while generating moderation: {e}',
                inner_exception=e
            )

        self._invoke_callback('on_moderation_generation_end', response=response, **context)

        return response

    async def run_async(
            self,
            request: str
    ) -> ModerationResponse:
        context = self._begin_run(generation_params=self.generation_params)

        await self._invoke_callback_async('on_moderation_generation_start', request=request, **context)

        try:
            generation_services = self._get_generation_services()

            response = ModerationResponse(model='', flagged=False)
            for generation_service in generation_services:
                response += await generation_service.run_async(request=request, generation_params=self.generation_params)
        except Exception as e:
            await self._invoke_callback_async('on_moderation_generation_error', error=e, **context)
            raise GenerationException(
                message=f'Error while generating moderation: {e}',
                inner_exception=e
            )

        await self._invoke_callback_async('on_moderation_generation_end', response=response, **context)

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
