import asyncio
from typing import Optional, Callable, AsyncIterator, AsyncGenerator, Any, Generator, List
from uuid import UUID, uuid4

from devtools import debug
from pydantic import Field, ConfigDict, model_validator, PrivateAttr

from skyframe.models.message import Message, MessageChunk
from skyframe.utils import logger
from .memory import ConversationMemory
from ..agents.models import AgentParams
from ..base import Runnable
from ..generators.audio import AudioGenerator
from ..generators.audio.models import AudioResponseChunk
from ..generators.audio.models import MessageAudio, MessageAudioChunk
from ..generators.text import TextGenerator
from ..generators.text.models import TextGenerationRequest, TextResponse, TextGenerationParams
from skyframe.runnables.models.run_info import RunContext


# @evaluatable
class Agent(Runnable):
    _id: str = PrivateAttr(default_factory=lambda: str(uuid4()))

    agent_params: AgentParams = Field(default_factory=AgentParams)

    memory: ConversationMemory = Field(default_factory=ConversationMemory)
    text_generator: TextGenerator = Field(default_factory=TextGenerator)
    audio_generator: Optional[AudioGenerator] = Field(default_factory=AudioGenerator)

    def __init__(self, **data):
        super().__init__(**data)
        self.text_generator.process_id = self.process_id
        if self.audio_generator:
            self.audio_generator.process_id = self.process_id

    # tools: List[Tool] = Field(default_factory=list)

    audio_task_holder: set = Field(default_factory=set)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    @model_validator(mode='after')
    def validate_text_generator(self) -> None:
        self.text_generator.generation_params.add_stop(['Human:', 'AI:'])

    @property
    def id(self) -> str:
        return self._id

    def try_set(self, **data: Any) -> List[str]:
        used = super().try_set(**data)
        used += self.agent_params.try_set(**data)
        used += self.text_generator.generation_params.try_set(**data)
        if self.audio_generator:
            used += self.audio_generator.generation_params.try_set(**data)
        return used

    def cleanup(self):
        del self.memory

        self.text_generator.cleanup()
        del self.text_generator

        if self.audio_generator:
            self.audio_generator.cleanup()
            del self.audio_generator

        super().cleanup()

    def __pretty__(self, fmt: Callable[[Any], Any], **kwargs: Any) -> Generator[Any, None, None]:
        for f in super().__pretty__(fmt, **kwargs):
            yield f
        yield 'Agent'
        yield 1
        yield f'Agent Params: {self.agent_params}'
        yield 0
        yield f'Text Generation Params: {self.text_generator.generation_params}'
        yield 0
        if self.audio_generator:
            yield f'Audio Generation Params: {self.audio_generator.generation_params}'
            yield 0
        yield 'Memory: '
        yield fmt(self.memory)
        if kwargs.get('request', None):
            yield 0
            yield f'Generating Response with request: {kwargs["request"]}'
        yield -1

    # @evaluate_async(eval_func_name='_eval_run')
    async def run_async(
            self,
            request: Optional[TextGenerationRequest] = None,
            *,
            audio_callback: Optional[Callable[[MessageAudio], None]] = None,
            run_id: Optional[UUID] = None,
    ) -> Message:
        run_ctx = self._begin_run(run_id=run_id)

        await self._invoke_callback_async('on_agent_generation_start', request=request, **run_ctx)

        try:
            if request:
                self.add_message(request)
            buffer = self.memory.load()

            if self.runnable_params.verbose:
                debug(self, request=request)

            text_response: TextResponse = await self.text_generator.run_async(buffer)
            message = Message.from_ai(content=text_response.content)

            if self.runnable_params.verbose:
                debug(message)

            if audio_callback:
                if not self.audio_generator:
                    logger.warning('Audio response callback provided but no audio generator is set. Audio will not be generated.')
                else:
                    audio_response = await self.audio_generator.run_async(text_response.content)
                    message_audio = MessageAudio(
                        message_id=message.id,
                        audio=audio_response.audio,
                        normalized_alignment=audio_response.normalized_alignment
                    )
                    audio_callback(message_audio)
                    message.audio_id = message_audio.id

            self.add_message(message)
        except Exception as e:
            await self._invoke_callback_async('on_agent_generation_error', error=e, **run_ctx)
            raise e

        await self._invoke_callback_async('on_agent_generation_end', response=message, **run_ctx)

        return message

    # @evaluate_async('_eval_run')
    async def run_async_stream(
            self,
            request: Optional[TextGenerationRequest] = None,
            *,
            injected_message: Optional[Message] = None,  # Use this to inject the correct starting message
            message_chunk_callback: Optional[Callable[[MessageChunk], None]] = None,
            audio_chunk_callback: Optional[Callable[[MessageAudioChunk], None]] = None,
            run_id: Optional[UUID] = None,
    ) -> Message:
        run_ctx = self._begin_run(run_id=run_id)

        await self._invoke_callback_async('on_agent_generation_start', request=request, **run_ctx)

        try:
            if request:
                self.add_message(request)
            buffer = self.memory.load()

            if self.runnable_params.verbose:
                debug(self, request=request)

            text_gen = self.text_generator.run_stream(buffer)
            text_queue = asyncio.Queue()

            message_chunks = []
            message = injected_message or Message.from_ai(content='')
            message_audio = None

            if audio_chunk_callback:
                if not self.audio_generator:
                    logger.warning('Audio response callback provided but no audio generator is set. Audio will not be generated.')
                else:
                    message_audio = MessageAudio(message_id=message.id)
                    text_iterator_for_audio = self._text_queue_iterator(text_queue)

                    audio_gen = self.audio_generator.run_stream(text_iterator_for_audio)

                    audio_task = asyncio.create_task(self._call_audio_callback_async(audio_gen, audio_chunk_callback, message_audio))
                    audio_task.add_done_callback(self.audio_task_holder.discard)
                    self.audio_task_holder.add(audio_task)

            if message_audio:
                message.audio_id = message_audio.id

            async for text_chunk in text_gen:
                if not text_chunk:
                    continue
                chunk = MessageChunk.of_message(
                    index=len(message_chunks),
                    message=message,
                    content=text_chunk.content or '',
                    is_final=text_chunk.is_final,
                )

                if message_chunk_callback:
                    message_chunk_callback(chunk)

                message_chunks.append(chunk)
                message += chunk
                if message_audio and chunk.content:
                    await text_queue.put(chunk.content)

                await self._invoke_callback_async('on_agent_generation_chunk', chunk=chunk, **run_ctx)

            if message_audio:
                await text_queue.put(None)  # Add the sentinel value to stop the audio iterator

            self.add_message(message)

            await self._invoke_callback_async('on_agent_generation_end', response=message, **run_ctx)
            return message
        except Exception as e:
            logger.exception(e)
            await self._invoke_callback_async('on_agent_generation_error', error=e, **run_ctx)
            raise e

    @staticmethod
    async def _call_audio_callback_async(
            audio_gen: AsyncGenerator[AudioResponseChunk, None],
            audio_chunk_callback: Callable[[MessageAudioChunk], None],
            message_audio: MessageAudio,
    ):
        index = 0
        async for audio_response_chunk in audio_gen:
            try:
                chunk = MessageAudioChunk.of_message_audio(
                    index=index,
                    message_audio=message_audio,
                    audio=audio_response_chunk.audio,
                    normalized_alignment=audio_response_chunk.normalized_alignment,
                    is_final=audio_response_chunk.is_final,
                )
                index += 1
                audio_chunk_callback(chunk)
            except Exception as e:
                logger.exception(e)
                raise e

    @staticmethod
    async def _text_queue_iterator(text_queue: asyncio.Queue) -> AsyncIterator[str]:
        while True:
            text_content = await text_queue.get()
            if text_content is None:  # Check for sentinel value
                break
            yield text_content

    async def _eval_run(self, *args, **kwargs):
        run_ctx = self._begin_run(parent_run_id=kwargs.get('run_id', None), eval_run=True)

        await self._invoke_callback_async('on_agent_generation_start', request=None, **run_ctx)

        try:
            buffer = self.memory.load()
            override_params = TextGenerationParams(stream=False)
            text_response: TextResponse = await self.text_generator.run_async(buffer, override_params=override_params)
            message = Message.from_ai(content=text_response.content)
        except Exception as e:
            await self._invoke_callback_async('on_agent_generation_error', error=e, **run_ctx)
            raise e

        await self._invoke_callback_async('on_agent_generation_end', response=message, **run_ctx)

        return message

    def add_message(self, message: TextGenerationRequest) -> None:
        self.memory.save(message)

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
            agent=self,
            message_list=self.memory.load(),
            **kwargs
        )

