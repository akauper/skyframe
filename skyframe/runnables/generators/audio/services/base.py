from abc import ABC, abstractmethod
from typing import AsyncGenerator, AsyncIterator

from ..models import AudioResponse, AudioGenerationParams, AudioResponseChunk


class BaseAudioGenerationService(ABC):

    @abstractmethod
    async def generate_async(
            self,
            request: str,
            generation_params: AudioGenerationParams
    ) -> AudioResponse:
        pass

    @abstractmethod
    def generate_stream_output(
            self,
            request: str,
            generation_params: AudioGenerationParams
    ) -> AsyncGenerator[AudioResponseChunk, None]:
        pass

    @abstractmethod
    def generate_stream_full_duplex(
            self,
            request: AsyncIterator[str],
            generation_params: AudioGenerationParams
    ) -> AsyncGenerator[AudioResponseChunk, None]:
        pass

    @classmethod
    def get_service(cls, service_name: str) -> 'BaseAudioGenerationService':
        if service_name == 'eleven_labs':
            from .eleven_labs import ElevenLabsGenerationService
            return ElevenLabsGenerationService()
        raise NotImplementedError(f'Audio Generation service: {service_name} is not implemented')

    @classmethod
    def import_dependencies(cls):
        pass
