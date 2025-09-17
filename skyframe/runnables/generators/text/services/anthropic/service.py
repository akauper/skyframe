from typing import AsyncGenerator, Optional, Union

import tiktoken
from anthropic import Anthropic, AsyncAnthropic, AsyncMessageStreamManager
from anthropic.types import Message as AnthropicMessage
from anthropic.types.message_create_params import MessageCreateParamsBase
from dotenv import load_dotenv

from skyframe import framework_settings
from skyframe import Message
from skyframe.utils import logger
from .converter import AnthropicGenerationConverter
from ..base import BaseTextGenerationService
from ...models import (
    TextGenerationParams,
    TextGenerationRequest,
    TextResponse,
    TextResponseChunk,
)


class AnthropicGenerationService(BaseTextGenerationService):
    client: AsyncAnthropic
    client_sync: Anthropic
    converter: AnthropicGenerationConverter
    default_model: str = framework_settings.runnables.generators.text.get_service_value('anthropic', 'default_model') or "claude-3-5-sonnet-20240620"

    def __init__(self):
        super().__init__()
        load_dotenv()
        self.client = AsyncAnthropic()
        self.client_sync = Anthropic()
        self.converter = AnthropicGenerationConverter()

    @staticmethod
    def _get_model_name(params: Optional[TextGenerationParams]) -> str:
        if params is None or params.model is None:
            return AnthropicGenerationService.default_model
        else:
            return params.model

    @staticmethod
    def get_token_count(
        request: TextGenerationRequest,
        generation_info: Optional[Union[str, TextGenerationParams]],
    ) -> int:
        if isinstance(generation_info, str):
            model = generation_info
        elif isinstance(generation_info, TextGenerationParams):
            model = generation_info.model
        else:
            logger.warning(
                f"get_token_count called without a model name. Using default model '{AnthropicGenerationService.default_model}'."
            )
            model = AnthropicGenerationService.default_model

        if isinstance(request, str):
            request_str = request
        elif isinstance(request, list):
            request_str = Message.join_as_string(request)
        elif isinstance(request, Message):
            request_str = request.to_string()
        else:
            logger.warning(f"Cannot get token count for request: {request}")
            return 0

        encoder = tiktoken.encoding_for_model(model_name=str(model))
        encoding = encoder.encode(request_str)
        return len(encoding)

    def _get_anthropic_params(
            self,
            request: TextGenerationRequest,
            generation_params: TextGenerationParams,
    ) -> MessageCreateParamsBase:
        if request is None:
            raise ValueError("TextGenerationRequest cannot be None")

        model = self._get_model_name(generation_params)

        logger.dev_debug(request)
        logger.dev_debug(generation_params)

        anthropic_params = self.converter.to_completion_create_params(
            request=request,
            generation_params=generation_params,
            model=model,
        )
        logger.dev_debug(anthropic_params)

        return anthropic_params

    def run(
        self,
        request: TextGenerationRequest,
        generation_params: TextGenerationParams,
    ) -> TextResponse:
        anthropic_params = self._get_anthropic_params(request, generation_params)

        anthropic_response: AnthropicMessage = self.client_sync.messages.create(
            **anthropic_params
        )
        logger.dev_debug(anthropic_response)

        response = self.converter.from_anthropic_response(anthropic_response)
        logger.dev_debug(response)

        return response

    async def run_async(
        self,
        request: TextGenerationRequest,
        generation_params: TextGenerationParams,
    ) -> TextResponse:
        anthropic_params = self._get_anthropic_params(request, generation_params)

        anthropic_response: AnthropicMessage = await self.client.messages.create(
            **anthropic_params
        )
        logger.dev_debug(anthropic_response)

        response = self.converter.from_anthropic_response(anthropic_response)
        logger.dev_debug(response)

        return response

    async def run_stream(
        self,
        request: TextGenerationRequest,
        generation_params: TextGenerationParams,
    ) -> AsyncGenerator[TextResponseChunk, None]:
        anthropic_params = self._get_anthropic_params(request, generation_params)

        stream: AsyncMessageStreamManager = self.client.messages.stream(
            **anthropic_params
        )

        gen = self.converter.from_async_stream(stream)

        return gen
