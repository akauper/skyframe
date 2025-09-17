from typing import Optional, Type, List, Dict, Any
from uuid import UUID

from skyframe.utils import logger

from .models.events import AgentStepEvent, AgentInputEvent, AgentResponseEvent, BaseStepEvent, TextGenStepEvent, TextGenInputEvent, TextGenResponseEvent
from .. import TextGenerator, TextGenerationParams, TextResponse
from ..models import Message
from ..runnables import BaseAsyncCallback, Runnable
from ..runnables import RunInfo, TextGenerationRequest, Agent


class EvaluationCallback(BaseAsyncCallback):
    runnable_type: Type[Runnable]
    _steps_dict: Dict[UUID, BaseStepEvent]

    def __init__(self, **data):
        super().__init__(**data)
        self._steps_dict = {}

    @property
    def steps(self) -> List[BaseStepEvent]:
        return list(self._steps_dict.values())

    def _valid_callback(self, callback_name: str) -> bool:
        return self.runnable_type.__name__.lower() in callback_name

    async def on_agent_generation_start(
            self,
            info: 'RunInfo',
            *,
            request: 'TextGenerationRequest',
            agent: Optional['Agent'] = None,
            message_list: Optional[List[Message]] = None,
            **kwargs,
    ):
        if not self._valid_callback('on_agent_generation_start'):
            return

        step = AgentStepEvent(
            run_id=info.run_id,
            parent_run_id=info.parent_run_id,
            input=AgentInputEvent(
                agent=agent,
                data=message_list[-1]
            )
        )
        self._steps_dict[info.run_id] = step

    async def on_agent_generation_end(
            self,
            info: 'RunInfo',
            *,
            response: Message,
            agent: Optional['Agent'] = None,
            message_list: Optional[List[Message]] = None,
            **kwargs,
    ):
        if not self._valid_callback('on_agent_generation_end'):
            return

        step = self._steps_dict.get(info.run_id, None)
        if step:
            step.response = AgentResponseEvent(
                data=response
            )
        else:
            logger.warning(f"Step not found for run_id: {info.run_id}")

    async def on_text_generation_start(
            self,
            info: 'RunInfo',
            *,
            request: 'TextGenerationRequest',
            generator: Optional['TextGenerator'] = None,
            generation_params: Optional['TextGenerationParams'] = None,
            **kwargs,
    ) -> Any:
        if not self._valid_callback('textgenerator'):
            return

        step = TextGenStepEvent(
            run_id=info.run_id,
            parent_run_id=info.parent_run_id,
            input=TextGenInputEvent(
                generator=generator,
                data=request
            )
        )
        self._steps_dict[info.run_id] = step

    async def on_text_generation_end(
            self,
            info: 'RunInfo',
            *,
            response: 'TextResponse',
            generator: Optional['TextGenerator'] = None,
            generation_params: Optional['TextGenerationParams'] = None,
            **kwargs,
    ) -> Any:
        if not self._valid_callback('textgenerator'):
            return

        step = self._steps_dict.get(info.run_id, None)
        if step:
            step.response = TextGenResponseEvent(
                data=response
            )
        else:
            logger.warning(f"Step not found for run_id: {info.run_id}")
