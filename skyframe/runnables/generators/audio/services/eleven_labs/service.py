import os
from typing import AsyncGenerator, AsyncIterator

from devtools import debug
from dotenv import load_dotenv

from .client import ElevenLabsClient
from .converter import ElevenLabsGenerationConverter
from ..base import BaseAudioGenerationService
from ...models import AudioResponse, AudioGenerationParams, AudioResponseChunk


class ElevenLabsGenerationService(BaseAudioGenerationService):
    client: ElevenLabsClient
    converter: ElevenLabsGenerationConverter

    def __init__(self):
        super().__init__()
        load_dotenv()
        api_key = os.environ.get('ELEVEN_LABS_API_KEY')
        self.client = ElevenLabsClient(api_key)
        self.converter = ElevenLabsGenerationConverter()

    async def generate_async(
            self,
            request: str,
            generation_params: AudioGenerationParams
    ) -> AudioResponse:
        if request is None:
            raise ValueError('AudioGenerationRequest cannot be None')

        eleven_labs_request = self.converter.to_request(request, generation_params)

        response = await self.client.generate_async(
            **eleven_labs_request
        )

        return response

    def generate_stream_output(
            self,
            request: str,
            generation_params: AudioGenerationParams
    ) -> AsyncGenerator[AudioResponseChunk, None]:
        if request is None:
            raise ValueError('AudioGenerationRequest cannot be None')

        eleven_labs_request = self.converter.to_request(request, generation_params)

        return self.client.generate_async_stream_output(**eleven_labs_request)

    def generate_stream_full_duplex(
            self,
            request: AsyncIterator[str],
            generation_params: AudioGenerationParams
    ) -> AsyncGenerator[AudioResponseChunk, None]:
        if request is None:
            raise ValueError('AudioGenerationRequest cannot be None')

        eleven_labs_request = self.converter.to_request(request, generation_params)
        debug(eleven_labs_request)

        return self.client.generate_async_stream_full_duplex(**eleven_labs_request)
