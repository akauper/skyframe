from typing import List, AsyncGenerator, TypeVar, Optional

from openai import AsyncStream
from openai.types import CompletionUsage as OpenAiCompletionUsage
from openai.types.chat import ChatCompletion, ChatCompletionTokenLogprob, ChatCompletionChunk, \
    ChatCompletionMessageParam, ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam, \
    ChatCompletionAssistantMessageParam
from openai.types.chat.chat_completion import Choice, ChoiceLogprobs
from openai.types.chat.chat_completion_chunk import Choice as ChunkChoice
from openai.types.chat.completion_create_params import CompletionCreateParamsBase

from skyframe.exceptions import ConversionException
from skyframe.models.message import Message, MessageRole
from skyframe.models.token_usage import TokenUsage
from ...models import TextResponse, TextChoice, TextGenerationParams, \
    TextResponseChunk, TextChoiceChunk, TextGenerationRequest, LogProb, TopLogprob

_T = TypeVar('_T')


class OpenAiGenerationConverter:
    """
    A class for converting between Quiply and OpenAI objects

    :raises ConversionException: If the conversion fails
    """

    @staticmethod
    def to_chat_completion_messages(request: TextGenerationRequest) -> List[ChatCompletionMessageParam]:
        """
        Converts a Quiply GenerationRequest object to a list of OpenAI ChatCompletionMessageParam objects

        :param request: The Quiply GenerationRequest object to convert
        :return: The converted list of OpenAI ChatCompletionMessageParam objects
        """
        try:
            if isinstance(request, Message):
                return [OpenAiGenerationConverter.to_chat_completion_message(request)]
            elif isinstance(request, list):
                return [OpenAiGenerationConverter.to_chat_completion_message(message) for message in request]
            elif isinstance(request, str):
                return [ChatCompletionUserMessageParam(
                    content=request,
                    role='user',
                )]
            else:
                raise ValueError(f"Unknown request type: {type(request)}")
        except Exception as e:
            raise ConversionException(
                OpenAiGenerationConverter,
                from_type=List[Message],
                to_type=List[ChatCompletionMessageParam],
                inner_exception=e
            )

    @staticmethod
    def to_chat_completion_message(message: Message) -> ChatCompletionMessageParam:
        """
        Converts a Quiply Message object to an OpenAI ChatCompletionMessageParam object

        :param message: The Quiply Message object to convert
        :return: The converted OpenAI ChatCompletionMessageParam object
        """
        try:
            if message.is_from(MessageRole.system):
                param = ChatCompletionSystemMessageParam(
                    content=message.content,
                    role='system',
                )
            elif message.is_from(MessageRole.user):
                param = ChatCompletionUserMessageParam(
                    content=message.content,
                    role='user',
                )
                if message.author_name and message.author_name != '':
                    param.setdefault('name', message.author_name)
            elif message.is_from(MessageRole.ai):
                param = ChatCompletionAssistantMessageParam(
                    content=message.content,
                    role='assistant',
                )
                if message.author_name and message.author_name != '':
                    param.setdefault('name', message.author_name)
            else:
                raise ValueError(f"Unknown message type: {message.type}")

            return param
        except Exception as e:
            raise ConversionException(
                OpenAiGenerationConverter,
                from_type=Message,
                to_type=ChatCompletionMessageParam,
                inner_exception=e
            )

    @staticmethod
    def to_completion_create_params(
            request: TextGenerationRequest,
            generation_params: TextGenerationParams,
            model: Optional[str] = None
    ) -> CompletionCreateParamsBase:
        """
        Converts a Quiply GenerationParams object to an OpenAI CompletionCreateParamsBase object

        :param request: The Quiply GenerationRequest object to convert
        :param generation_params: The Quiply GenerationParams object to convert
        :param model: The name of the model to use for the conversion
        :return: The converted OpenAI CompletionCreateParamsBase object
        """
        try:
            if model is None and generation_params.model is None:
                raise ValueError("Must provide either generation_params or model_name")

            params_dict = generation_params.model_dump(exclude_none=True)

            response_format = params_dict.get('response_format', None)
            if response_format is not None:
                params_dict['response_format'] = {'type': response_format}

            if model is not None:
                params_dict['model'] = model

            return CompletionCreateParamsBase(
                messages=OpenAiGenerationConverter.to_chat_completion_messages(request),
                **params_dict
            )
        except Exception as e:
            raise ConversionException(
                OpenAiGenerationConverter,
                from_type=TextGenerationParams,
                to_type=CompletionCreateParamsBase,
                inner_exception=e
            )

    @staticmethod
    def from_chat_completion(chat_completion: ChatCompletion) -> TextResponse:
        """
        Converts an OpenAI ChatCompletion object to a Quiply TextResponse object

        :param chat_completion: The OpenAI ChatCompletion object to convert
        :return: The converted Quiply TextResponse object
        """
        try:
            return TextResponse(
                id=chat_completion.id,
                choices=[OpenAiGenerationConverter.from_choice(choice) for choice in chat_completion.choices],
                created_at=chat_completion.created,
                model=chat_completion.model,
                system_fingerprint=chat_completion.system_fingerprint,
                token_usage=OpenAiGenerationConverter.from_usage(chat_completion.usage, chat_completion.model),
            )
        except Exception as e:
            raise ConversionException(
                OpenAiGenerationConverter,
                from_type=ChatCompletion,
                to_type=TextResponse,
                inner_exception=e
            )

    @staticmethod
    def from_choice(choice: Choice) -> TextChoice:
        """
        Converts an OpenAI Choice object to a Quiply TextChoice object

        :param choice: The OpenAI Choice object to convert
        :return: The converted Quiply TextChoice object
        """
        try:
            return TextChoice(
                index=choice.index,
                content=choice.message.content,
                finish_reason=choice.finish_reason,
                role=choice.message.role,
                logprobs=OpenAiGenerationConverter.from_choice_logprobs(choice.logprobs),
            )
        except Exception as e:
            raise ConversionException(
                OpenAiGenerationConverter,
                from_type=Choice,
                to_type=TextChoice,
                inner_exception=e
            )

    @staticmethod
    def from_choice_logprobs(choice_logprobs: ChoiceLogprobs) -> List[LogProb]:
        """
        Converts an OpenAI ChoiceLogprobs object to a list of Quiply LogProb objects

        :param choice_logprobs: The OpenAI ChoiceLogprobs object to convert
        :return: The converted list of Quiply LogProb objects
        """
        try:
            if choice_logprobs is None or choice_logprobs.content is None:
                return []
            return [OpenAiGenerationConverter.from_completion_logprob(completion_logprob) for completion_logprob in choice_logprobs.content]
        except Exception as e:
            raise ConversionException(
                OpenAiGenerationConverter,
                from_type=ChoiceLogprobs,
                to_type=List[LogProb],
                inner_exception=e
            )

    @staticmethod
    def from_completion_logprob(completion_logprob: ChatCompletionTokenLogprob) -> LogProb:
        """
        Converts an OpenAI ChatCompletionTokenLogprob object to a Quiply LogProb object

        :param completion_logprob: The OpenAI ChatCompletionTokenLogprob object to convert
        :return: The converted Quiply LogProb object
        """
        try:
            return LogProb(
                token=completion_logprob.token,
                bytes=completion_logprob.bytes,
                logprob=completion_logprob.logprob,
                top_logprobs=[TopLogprob(
                    token=top_logprob.token,
                    bytes=top_logprob.bytes,
                    logprob=top_logprob.logprob
                ) for top_logprob in completion_logprob.top_logprobs]
            )
        except Exception as e:
            raise ConversionException(
                OpenAiGenerationConverter,
                from_type=ChatCompletionTokenLogprob,
                to_type=LogProb,
                inner_exception=e
            )

    @staticmethod
    def from_usage(usage: OpenAiCompletionUsage, model_name: Optional[str] = None) -> TokenUsage:
        """
        Converts an OpenAI CompletionUsage object to a Quiply TokenUsage object

        :param usage: The OpenAI CompletionUsage object to convert
        :param model_name: The name of the model used for the conversion (Used for cost calculation)
        :return: The converted Quiply TextResponseUsage object
        """
        try:
            if model_name is not None:
                from .service import OpenAiGenerationService
                total_cost = OpenAiGenerationService.calculate_cost(usage.total_tokens, model_name)
                prompt_cost = OpenAiGenerationService.calculate_cost(usage.prompt_tokens, model_name)
                completion_cost = OpenAiGenerationService.calculate_cost(usage.completion_tokens, model_name)
            else:
                total_cost = 0
                prompt_cost = 0
                completion_cost = 0

            return TokenUsage(
                total=usage.total_tokens,
                prompt=usage.prompt_tokens,
                completion=usage.completion_tokens,
                
                total_cost=total_cost,
                prompt_cost=prompt_cost,
                completion_cost=completion_cost
            )
        except Exception as e:
            raise ConversionException(
                OpenAiGenerationConverter,
                from_type=OpenAiCompletionUsage,
                to_type=TokenUsage,
                inner_exception=e
            )

    @staticmethod
    async def from_async_stream(stream: AsyncStream[ChatCompletionChunk]) -> AsyncGenerator[TextResponseChunk, None]:
        """
        Converts an OpenAI AsyncStream of ChatCompletionChunk objects to a Quiply AsyncGenerator of TextResponseChunk objects

        :param stream: The OpenAI AsyncStream of ChatCompletionChunk objects to convert
        :return: The converted Quiply AsyncGenerator of TextResponseChunk objects
        """
        try:
            id = ''
            model = ''
            index = 0
            created = 0
            async for item in stream:
                id = item.id
                model = item.model
                created = item.created
                yield OpenAiGenerationConverter.from_chat_completion_chunk(item, index)
                index += 1

            yield TextResponseChunk(
                id=id,
                index=index,
                created_at=created,
                model=model,
                is_final=True
            )
        except Exception as e:
            print(e)
            raise ConversionException(
                OpenAiGenerationConverter,
                from_type=AsyncStream[ChatCompletionChunk],
                to_type=AsyncGenerator[TextResponseChunk, None],
                inner_exception=e
            )

    @staticmethod
    def from_chat_completion_chunk(chat_chunk: ChatCompletionChunk, index: int) -> TextResponseChunk:
        """
        Converts an OpenAI ChatCompletionChunk object to a Quiply TextResponseChunk object

        :param chat_chunk: The OpenAI ChatCompletionChunk object to convert
        :param index: The index of the chunk in the stream of chunks
        :return: The converted Quiply TextResponseChunk object
        """
        try:
            return TextResponseChunk(
                id=chat_chunk.id,
                index=index,
                choices=[OpenAiGenerationConverter.from_chunk_choice(choice) for choice in chat_chunk.choices],
                created_at=chat_chunk.created,
                model=chat_chunk.model,
                system_fingerprint=chat_chunk.system_fingerprint,
            )
        except Exception as e:
            raise ConversionException(
                OpenAiGenerationConverter,
                from_type=ChatCompletionChunk,
                to_type=TextResponseChunk,
                inner_exception=e
            )

    @staticmethod
    def from_chunk_choice(choice: ChunkChoice) -> TextChoiceChunk:
        """
        Converts an OpenAI ChunkChoice object to a Quiply TextChoiceChunk object

        :param choice: The OpenAI ChunkChoice object to convert
        :return: The converted Quiply TextChoiceChunk object
        """
        try:
            return TextChoiceChunk(
                index=choice.index,
                content=choice.delta.content,
                finish_reason=choice.finish_reason,
                role=choice.delta.role,
                logprobs=OpenAiGenerationConverter.from_choice_logprobs(choice.logprobs),
            )
        except Exception as e:
            raise ConversionException(
                OpenAiGenerationConverter,
                from_type=ChunkChoice,
                to_type=TextChoiceChunk,
                inner_exception=e
            )