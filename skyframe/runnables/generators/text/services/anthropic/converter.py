import time
from typing import Optional, List, Literal, AsyncGenerator

from anthropic import AsyncStream, AsyncMessageStreamManager
from anthropic.types import RawMessageStreamEvent
from anthropic.types.message import Message as AnthropicMessage, ContentBlock
from anthropic.types.message_create_params import (
    MessageCreateParams,
    MessageCreateParamsBase,
)
from anthropic.types.message_param import MessageParam
from anthropic.types.usage import Usage
from devtools import debug
from skyframe.utils import logger

from skyframe import Message, MessageRole, TokenUsage, TextResponseChunk, TextChoiceChunk
from skyframe.exceptions import ConversionException
from ...models import (
    TextResponse,
    TextChoice,
    TextGenerationParams,
    TextGenerationRequest,
)

STOP_REASON = Literal["end_turn", "max_tokens", "stop_sequence", "tool_use"]


class AnthropicGenerationConverter:
    @staticmethod
    def to_anthropic_message_params(
        request: TextGenerationRequest,
    ) -> List[MessageParam]:
        """
        Converts a Quiply GenerationRequest object to a list of Anthropic MessageParam objects

        :param request: The Quiply GenerationRequest object to convert
        :return: The converted list of Anthropic MessageParam objects
        """
        try:
            if isinstance(request, Message):
                return [
                    AnthropicGenerationConverter.to_anthropic_message_param(request)
                ]
            elif isinstance(request, list):
                return [
                    AnthropicGenerationConverter.to_anthropic_message_param(message)
                    for message in request
                ]
            elif isinstance(request, str):
                return [{"content": request, "role": "user"}]
            else:
                raise ValueError(f"Unknown request type: {type(request)}")
        except Exception as e:
            raise ConversionException(
                AnthropicGenerationConverter,
                from_type=List[Message],
                to_type=List[MessageParam],
                inner_exception=e,
            )

    @staticmethod
    def to_anthropic_message_param(message: Message) -> MessageParam:
        """
        Converts a Quiply Message object to an Anthropic MessageParam object

        :param message: The Quiply Message object to convert
        :return: The converted Anthropic MessageParam object
        """
        try:
            param: MessageParam = {
                "content": message.content,
                "role": "user" if message.role == MessageRole.user else "assistant",
            }
            return param
        except Exception as e:
            raise ConversionException(
                AnthropicGenerationConverter,
                from_type=Message,
                to_type=MessageParam,
                inner_exception=e,
            )

    @staticmethod
    def to_completion_create_params(
        request: TextGenerationRequest,
        generation_params: TextGenerationParams,
        model: Optional[str] = None,
    ) -> MessageCreateParamsBase:
        """
        Converts a Quiply GenerationParams object to an Anthropic MessageCreateParamsBase object

        :param request: The Quiply GenerationRequest object to convert
        :param generation_params: The Quiply GenerationParams object to convert
        :param model: The name of the model to use for the conversion
        :return: The converted Anthropic MessageCreateParamsBase object
        """
        try:
            if model is None and generation_params.model is None:
                raise ValueError("Must provide either generation_params or model_name")

            system: Optional[str] = None

            if isinstance(request, list):
                first_message: Message = request[0]
                if first_message.role == MessageRole.system:
                    system = first_message.content
                    request = request[1:]

                if len(request) == 0:
                    logger.warning("Anthropic Request messages is empty. This is not allowed. Adding a message with 'Start the conversation' content.")
                    request.append(Message(content="Start the conversation", role=MessageRole.user))
            elif isinstance(request, Message):
                if request.role != MessageRole.user:
                    raise ValueError("First message must be from the user for anthropic")

            if not generation_params.stop:
                stop = None
            elif isinstance(generation_params.stop, list):
                stop = generation_params.stop
            else:
                stop = [generation_params.stop]

            params: MessageCreateParamsBase = {
                "max_tokens": generation_params.max_tokens
                if generation_params.max_tokens is not None
                else 1024,
                "messages": AnthropicGenerationConverter.to_anthropic_message_params(
                    request
                ),
                "model": model or str(generation_params.model),
            }

            if stop:
                params["stop_sequences"] = stop
            if system:
                params["system"] = system
            if generation_params.temperature:
                params["temperature"] = generation_params.temperature
            if generation_params.top_k:
                params["top_k"] = generation_params.top_k
            if generation_params.top_p:
                params["top_p"] = generation_params.top_p

            return params

        except Exception as e:
            raise ConversionException(
                AnthropicGenerationConverter,
                from_type=TextGenerationParams,
                to_type=MessageCreateParams,
                inner_exception=e,
            )

    @staticmethod
    def from_anthropic_response(response: AnthropicMessage) -> TextResponse:
        """
        Converts an Anthropic Message object to a Quiply TextResponse object

        :param response: The Anthropic Message object to convert
        :return: The converted Quiply TextResponse object
        """
        try:
            return TextResponse(
                id=response.id,
                choices=[
                    AnthropicGenerationConverter.from_content_block(
                        content_block, index, response.stop_reason
                    )
                    for index, content_block in enumerate(response.content)
                ],
                created_at=int(time.time()),
                model=response.model,
                token_usage=AnthropicGenerationConverter.from_usage(response.usage, response.model),
            )
        except Exception as e:
            raise ConversionException(
                AnthropicGenerationConverter,
                from_type=AnthropicMessage,
                to_type=TextResponse,
                inner_exception=e,
            )

    @staticmethod
    def from_content_block(
        content_block: ContentBlock, index: int, stop_reason: Optional[STOP_REASON]
    ) -> TextChoice:
        """
        Converts an Anthropic ContentBlock object to a Quiply TextChoice object

        :param content_block: The Anthropic ContentBlock object to convert
        :param index: The index of the response in the list of responses
        :param stop_reason: The reason the model stopped generating tokens
        :return: The converted Quiply TextChoice object
        """
        try:
            return TextChoice(
                index=index,
                content=content_block.text,
                role="assistant",
                finish_reason=stop_reason,
            )
        except Exception as e:
            raise ConversionException(
                AnthropicGenerationConverter,
                from_type=ContentBlock,
                to_type=TextChoice,
                inner_exception=e,
            )

    @staticmethod
    def from_usage(usage: Usage, model_name: Optional[str] = None) -> TokenUsage:
        """
        Converts an Anthropic Usage object to a Quiply TokenUsage object

        :param usage: The Anthropic Usage object to convert
        :param model_name: The name of the model used for the conversion
        :return: The converted Quiply TokenUsage object
        """
        try:
            from .service import AnthropicGenerationService
            token_usage = TokenUsage(
                total=usage.input_tokens + usage.output_tokens,
                prompt=usage.input_tokens,
                completion=usage.output_tokens,
            )
            cost_per_input_token = AnthropicGenerationService.get_cost_per_input_token(model_name)
            cost_per_output_token = AnthropicGenerationService.get_cost_per_output_token(model_name)
            token_usage.calculate_cost(cost_per_input_token, cost_per_output_token)
            return token_usage
        except Exception as e:
            raise ConversionException(
                AnthropicGenerationConverter,
                from_type=Usage,
                to_type=TokenUsage,
                inner_exception=e,
            )

    @staticmethod
    async def from_async_stream(stream_manager: AsyncMessageStreamManager) -> AsyncGenerator[TextResponseChunk, None]:
        """
        Converts an Anthropic AsyncMessageStreamManager object to a Quiply AsyncGenerator of TextResponseChunk objects

        :param stream_manager: The Anthropic AsyncMessageStreamManager object to convert
        :return: The converted Quiply AsyncGenerator of TextResponseChunk objects
        """
        try:
            async with stream_manager as stream:
                id = ''
                model = ''
                index = 0
                async for event in stream:
                    # debug(event)
                    if event.type == 'message_start':
                        message: AnthropicMessage = event.message
                        id = message.id
                        model = message.model

                    if event.type == 'text':
                        yield TextResponseChunk(
                            id=id,
                            index=index,
                            choices=[TextChoiceChunk(
                                index=0,
                                content=event.text,
                                role='assistant',
                            )],
                            created_at=int(time.time()),
                            model=model
                        )
                        index += 1

                yield TextResponseChunk(
                    id=id,
                    index=index + 1,
                    created_at=int(time.time()),
                    model=model,
                    is_final=True,
                )
        except Exception as e:
            debug(e)
            raise ConversionException(
                AnthropicGenerationConverter,
                from_type=AsyncStream[RawMessageStreamEvent],
                to_type=AsyncGenerator[TextResponseChunk, None],
                inner_exception=e,
            )