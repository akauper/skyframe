from typing import Dict, Any, ClassVar

from pydantic import Field

from skyframe.models import TokenUsage
from skyframe.utils import StopwatchContext
from skyframe.runnables.agents import Agent
from ..base_input import BaseInput
from skyframe.evaluation.results.input_result import InputResult
from skyframe.evaluation.callback import EvaluationCallback
from skyframe.evaluation.context import EvaluationContext

# check if we have skyframe.automation first
try:
    import skyframe.automation as automation  # noqa
    AUTOMATION_AVAILABLE = True
except ImportError:
    AUTOMATION_AVAILABLE = False


class ConversationGeneratorInput(BaseInput):
    type: ClassVar[str] = "conversation-generator"
    params: Dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data):
        if "value" not in data:
            data["value"] = "default"
        super().__init__(**data)

    async def resolve_async(self, input: Dict[str, str]) -> InputResult:
        if not AUTOMATION_AVAILABLE:
            raise ImportError("skyframe.automation is required for ConversationGeneratorInput but is not installed.")

        async with StopwatchContext() as sw:
            callback = EvaluationCallback(runnable_type=Agent)
            config = automation.AutoConversationConfig.model_validate(self.params)
            config.agent_callbacks = [callback]

            auto_conversation = automation.AutoConversation(config)
            with EvaluationContext(key=self.value):
                output = await auto_conversation.run_async()

        return InputResult(
            resolvable=self,

            raw_template=self.value,
            vars=input,
            rendered_template='',
            value=output.conversation,

            steps=callback.steps,

            latency_ms=sw.elapsed_ms_int,
            token_usage=TokenUsage() # TODO: Add token_usage
        )
