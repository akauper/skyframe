import os
from ..base import BaseAudioGenerationService
from elevenlabs.client import AsyncElevenLabs
from dotenv import load_dotenv
from ...models import AudioResponse, AudioGenerationParams
from .converter import ElevenLabsGenerationConverter


class ElevenLabsGenerationService(BaseAudioGenerationService):
    client: AsyncElevenLabs
    converter: ElevenLabsGenerationConverter

    def __init__(self):
        super().__init__()
        load_dotenv()
        api_key = os.environ.get('ELEVEN_LABS_API_KEY')
        self.client = AsyncElevenLabs(api_key=api_key)


    async def generate_async(
            self,
            request: str,
            generation_params: AudioGenerationParams
    ) -> AudioResponse:
        if request is None:
            raise ValueError('AudioGenerationRequest cannot be None')

        eleven_labs_request = self.converter.to_request(request, generation_params)

        response = await self.client.generate(**eleven_labs_request)

        return response
