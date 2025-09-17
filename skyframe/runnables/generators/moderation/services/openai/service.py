import os

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI
from openai.types import ModerationCreateResponse

from skyframe.utils import logger
from .converter import OpenaiModerationConverter
from ..base import BaseModerationService
from ...models import ModerationResponse, ModerationGenerationParams


class OpenaiModerationService(BaseModerationService):
    client: AsyncOpenAI
    client_sync: OpenAI
    converter: OpenaiModerationConverter
    default_model: str = 'text-moderation-stable'

    def __init__(self):
        super().__init__()
        load_dotenv()
        api_key = os.environ.get('OPENAI_API_KEY')
        self.client = AsyncOpenAI(api_key=api_key)
        self.client_sync = OpenAI(api_key=api_key)
        self.converter = OpenaiModerationConverter()

    def run(
            self,
            request: str,
            generation_params: ModerationGenerationParams
    ) -> ModerationResponse:
        if request is None:
            raise ValueError('ModerationRequest cannot be None')

        moderation_create_response: ModerationCreateResponse = self.client_sync.moderations.create(
            input=request,
            model=self.default_model
        )

        logger.dev_debug(moderation_create_response)

        response = self.converter.from_moderation_create_response(moderation_create_response)

        logger.dev_debug(response)

        return response

    async def run_async(
            self,
            request: str,
            generation_params: ModerationGenerationParams
    ) -> ModerationResponse:
        if request is None:
            raise ValueError('ModerationRequest cannot be None')

        moderation_create_response: ModerationCreateResponse = await self.client.moderations.create(
            input=request,
            model=self.default_model
        )

        logger.dev_debug(moderation_create_response)

        response = self.converter.from_moderation_create_response(moderation_create_response)

        logger.dev_debug(response)

        return response
