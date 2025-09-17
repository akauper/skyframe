from abc import ABC
from typing import Any, Optional, TYPE_CHECKING, List

from pydantic import BaseModel

from skyframe.models.message import Message

if TYPE_CHECKING:
    from .run_info import RunInfo
    from ..base import Runnable
    from ..agents.agent import Agent
    from .. import generators as gen


class BaseAsyncCallback(BaseModel, ABC):
    async def on_any_start(
            self,
            callback_name: str,
            info: 'RunInfo',
            *,
            runnable: Optional['Runnable'] = None,
            **kwargs,
    ) -> Any:
        pass

    async def on_any_end(
            self,
            callback_name: str,
            info: 'RunInfo',
            *,
            runnable: Optional['Runnable'] = None,
            **kwargs,
    ) -> Any:
        pass

    async def on_any_error(
            self,
            callback_name: str,
            info: 'RunInfo',
            *,
            error: Exception,
            runnable: Optional['Runnable'] = None,
            **kwargs,
    ) -> Any:
        pass

    async def on_text_generation_start(
            self,
            info: 'RunInfo',
            *,
            request: 'gen.TextGenerationRequest',
            generator: Optional['gen.TextGenerator'] = None,
            generation_params: Optional['gen.TextGenerationParams'] = None,
            **kwargs,
    ) -> Any:
        pass

    async def on_text_generation_chunk(
            self,
            info: 'RunInfo',
            *,
            chunk: 'gen.TextResponseChunk',
            generator: Optional['gen.TextGenerator'] = None,
            **kwargs,
    ) -> Any:
        pass

    async def on_text_generation_end(
            self,
            info: 'RunInfo',
            *,
            response: 'gen.TextResponse',
            generator: Optional['gen.TextGenerator'] = None,
            **kwargs,
    ) -> Any:
        pass

    async def on_text_generation_error(
            self,
            info: 'RunInfo',
            *,
            error: Exception,
            generator: Optional['gen.TextGenerator'] = None,
            **kwargs,
    ) -> Any:
        pass

    async def on_audio_generation_start(
            self,
            info: 'RunInfo',
            *,
            request: 'gen.AudioGenerationRequest',
            generator: Optional['gen.AudioGenerator'] = None,
            generation_params: Optional['gen.AudioGenerationParams'] = None,
            **kwargs,
    ):
        pass

    async def on_audio_generation_chunk(
            self,
            info: 'RunInfo',
            *,
            chunk: 'gen.AudioResponseChunk',
            generator: Optional['gen.AudioGenerator'] = None,
            **kwargs,
    ):
        pass

    async def on_audio_generation_end(
            self,
            info: 'RunInfo',
            *,
            response: 'gen.AudioResponse',
            generator: Optional['gen.AudioGenerator'] = None,
            **kwargs,
    ):
        pass

    async def on_audio_generation_error(
            self,
            info: 'RunInfo',
            *,
            error: Exception,
            generator: Optional['gen.AudioGenerator'] = None,
            **kwargs,
    ):
        pass

    async def on_moderation_generation_start(
            self,
            info: 'RunInfo',
            *,
            request: str,
            generator: Optional['gen.ModerationGenerator'] = None,
            generation_params: Optional['gen.ModerationGenerationParams'] = None,
            **kwargs,
    ):
        pass

    async def on_moderation_generation_end(
            self,
            info: 'RunInfo',
            *,
            response: Any,
            generator: Optional['gen.ModerationGenerator'] = None,
            **kwargs,
    ):
        pass

    async def on_moderation_generation_error(
            self,
            info: 'RunInfo',
            *,
            error: Exception,
            generator: Optional['gen.ModerationGenerator'] = None,
            **kwargs,
    ):
        pass

    async def on_speech_to_text_generation_start(
            self,
            info: 'RunInfo',
            *,
            request: 'gen.SpeechToTextRequest',
            generator: Optional['gen.SpeechToTextGenerator'] = None,
            generation_params: Optional['gen.SpeechToTextGenerationParams'] = None,
            **kwargs,
    ):
        pass

    async def on_speech_to_text_generation_chunk(
            self,
            info: 'RunInfo',
            *,
            chunk: 'gen.SpeechToTextResponseChunk',
            generator: Optional['gen.SpeechToTextGenerator'] = None,
            **kwargs,
    ):
        pass

    async def on_speech_to_text_generation_end(
            self,
            info: 'RunInfo',
            *,
            response: 'gen.SpeechToTextResponse',
            generator: Optional['gen.SpeechToTextGenerator'] = None,
            **kwargs,
    ):
        pass

    async def on_speech_to_text_generation_error(
            self,
            info: 'RunInfo',
            *,
            error: Exception,
            generator: Optional['gen.SpeechToTextGenerator'] = None,
            **kwargs,
    ):
        pass

    async def on_agent_generation_start(
            self,
            info: 'RunInfo',
            *,
            request: 'gen.TextGenerationRequest',
            agent: Optional['Agent'] = None,
            message_list: Optional[List[Message]] = None,
            **kwargs,
    ):
        pass

    async def on_agent_generation_action(
            self,
            info: 'RunInfo',
            *,
            action: Any,
            agent: Optional['Agent'] = None,
            message_list: Optional[List[Message]] = None,
            **kwargs,
    ):
        pass

    async def on_agent_generation_chunk(
            self,
            info: 'RunInfo',
            *,
            chunk: 'gen.TextResponseChunk',
            agent: Optional['Agent'] = None,
            message_list: Optional[List[Message]] = None,
            **kwargs,
    ):
        pass

    async def on_agent_generation_end(
            self,
            info: 'RunInfo',
            *,
            response: Message,
            agent: Optional['Agent'] = None,
            message_list: Optional[List[Message]] = None,
            **kwargs,
    ):
        pass

    async def on_agent_generation_error(
            self,
            info: 'RunInfo',
            *,
            error: Exception,
            agent: Optional['Agent'] = None,
            message_list: Optional[List[Message]] = None,
            **kwargs,
    ):
        pass
