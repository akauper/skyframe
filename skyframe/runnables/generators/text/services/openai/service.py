import os
from typing import AsyncGenerator, Optional, Union

import tiktoken
from dotenv import load_dotenv
from openai import AsyncOpenAI, AsyncStream, OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types.chat.completion_create_params import CompletionCreateParamsBase

from skyframe import framework_settings
from skyframe.models.message import Message
from skyframe.utils import logger
from .converter import OpenAiGenerationConverter
from ..base import BaseTextGenerationService
from ...models import (
    TextGenerationParams,
    TextGenerationRequest,
    TextResponse,
    TextResponseChunk,
)

MAX_OUTPUT_TOKENS: int = 1024


class OpenAiGenerationService(BaseTextGenerationService):
    client: AsyncOpenAI
    client_sync: OpenAI
    converter: OpenAiGenerationConverter
    default_model: str = framework_settings.runnables.generators.text.get_service_value('openai', 'default_model') or "gpt-4o"

    def __init__(self):
        super().__init__()
        load_dotenv()
        api_key = os.environ.get("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=api_key)
        self.client_sync = OpenAI(api_key=api_key)
        self.converter = OpenAiGenerationConverter()

    @staticmethod
    def _get_model_name(params: Optional[TextGenerationParams]) -> str:
        if params is None or params.model is None:
            return OpenAiGenerationService.default_model
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
                f"get_token_count called without a model name. Using default model '{OpenAiGenerationService.default_model}'."
            )
            model = OpenAiGenerationService.default_model

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

    def _get_openai_params(
            self,
            request: TextGenerationRequest,
            generation_params: TextGenerationParams,
    ) -> CompletionCreateParamsBase:
        if request is None:
            raise ValueError("TextGenerationRequest cannot be None")

        model = self._get_model_name(generation_params)

        logger.dev_debug(request)
        logger.dev_debug(generation_params)

        openai_params = self.converter.to_completion_create_params(
            request=request,
            generation_params=generation_params,
            model=model
        )
        logger.dev_debug(openai_params)

        return openai_params

    def run(
        self,
        request: TextGenerationRequest,
        generation_params: TextGenerationParams,
    ) -> TextResponse:
        openai_params = self._get_openai_params(request, generation_params)

        chat_completion: ChatCompletion = self.client_sync.chat.completions.create(
            **openai_params
        )

        logger.dev_debug(chat_completion)

        response = self.converter.from_chat_completion(chat_completion)

        logger.dev_debug(response)

        return response

    async def run_async(
        self,
        request: TextGenerationRequest,
        generation_params: TextGenerationParams,
    ) -> TextResponse:
        openai_params = self._get_openai_params(request, generation_params)

        chat_completion: ChatCompletion = await self.client.chat.completions.create(
            **openai_params
        )

        logger.dev_debug(chat_completion)

        response = self.converter.from_chat_completion(chat_completion)

        logger.dev_debug(response)

        return response

    async def run_stream(
        self,
        request: TextGenerationRequest,
        generation_params: TextGenerationParams,
    ) -> AsyncGenerator[TextResponseChunk, None]:
        generation_params.stream = True
        openai_params = self._get_openai_params(request, generation_params)

        stream: AsyncStream[
            ChatCompletionChunk
        ] = await self.client.chat.completions.create(**openai_params)

        logger.dev_debug(stream)

        gen = self.converter.from_async_stream(stream)

        logger.dev_debug(gen)

        return gen
