from typing import TypeVar, AsyncGenerator, List, AsyncIterator, Any, ClassVar
from uuid import UUID

from skyframe.exceptions import GenerationException
from skyframe.runnables.models import RunContext
from .models import (
    AudioGenerationParams,
    AudioGenerationRequest,
    AudioResponse,
    AudioResponseChunk,
)
from .services import BaseAudioGenerationService, get_audio_generation_service
from ..base import BaseGenerator

TGenerationService = TypeVar("TGenerationService", bound=BaseAudioGenerationService)


class AudioGenerator(BaseGenerator[AudioGenerationParams]):
    # service_name: str = Field(default=_DEFAULT_SERVICE_NAME)
    # generation_params: AudioGenerationParams = Field(default_factory=AudioGenerationParams)

    generator_name: ClassVar[str] = "audio"

    def cleanup(self):
        del self.generation_params
        super().cleanup()

    def try_set(self, **data: Any) -> List[str]:
        used = super().try_set(**data)
        if "service_name" in data:
            self.service_name = data["service_name"]
            used.append("service_name")
        used += self.generation_params.try_set(**data)
        return used

    def _get_generation_service(self) -> TGenerationService:
        try:
            return get_audio_generation_service(self.service_name)
        except NotImplementedError as e:
            raise GenerationException(
                message=f"Generation service {self.service_name} is not implemented",
                inner_exception=e,
            )

    async def run_async(
        self,
        request: str,
    ) -> AudioResponse:
        run_ctx = self._begin_run(generation_params=self.generation_params)
        generation_service = self._get_generation_service()

        await self._invoke_callback_async(
            "on_audio_generation_start", request=request, **run_ctx
        )

        try:
            response = await generation_service.generate_async(
                request=request, generation_params=self.generation_params
            )
        except Exception as e:
            await self._invoke_callback_async(
                "on_audio_generation_error", error=e, **run_ctx
            )
            raise GenerationException(
                message=f"Error while generating audio: {e}", inner_exception=e
            )

        await self._invoke_callback_async(
            "on_audio_generation_end", response=response, **run_ctx
        )

        return response

    async def run_stream(
        self,
        request: AudioGenerationRequest,
    ) -> AsyncGenerator[AudioResponseChunk, None]:
        run_ctx = self._begin_run(generation_params=self.generation_params)
        generation_service = self._get_generation_service()

        await self._invoke_callback_async(
            "on_audio_generation_start", request=request, **run_ctx
        )

        try:
            if isinstance(request, str):
                generator = generation_service.generate_stream_output(
                    request, generation_params=self.generation_params
                )
            elif isinstance(request, AsyncIterator):
                generator = generation_service.generate_stream_full_duplex(
                    request, generation_params=self.generation_params
                )
            else:
                raise ValueError(f"Unsupported AudioGenerationRequest: {type(request)}")
        except Exception as e:
            await self._invoke_callback_async(
                "on_audio_generation_error", error=e, **run_ctx
            )
            raise GenerationException(
                message=f"Error while generating audio stream: {e}", inner_exception=e
            )

        chunks: List[AudioResponseChunk] = []

        async for chunk in generator:
            chunks.append(chunk)
            await self._invoke_callback_async(
                "on_audio_generation_chunk", chunk=chunk, **run_ctx
            )
            yield chunk

        response = AudioResponse.from_chunks(chunks)

        await self._invoke_callback_async(
            "on_audio_generation_end", response=response, **run_ctx
        )

    def _begin_run(
        self, *, run_id: UUID = None, parent_run_id: UUID = None, **kwargs
    ) -> RunContext:
        return super()._begin_run(
            run_id=run_id, parent_run_id=parent_run_id, generator=self, **kwargs
        )
