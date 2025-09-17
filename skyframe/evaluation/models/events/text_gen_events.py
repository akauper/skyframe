from typing import Optional

from pydantic import Field, ConfigDict

from .base_events import BaseInputEvent, BaseActionEvent, BaseResponseEvent, BaseStepEvent
from skyframe.runnables.generators.text import TextGenerator
from skyframe.runnables.generators.text.models import TextGenerationRequest, TextResponse


class TextGenInputEvent(BaseInputEvent):
    data: TextGenerationRequest
    generator: Optional[TextGenerator] = Field(default=None)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            TextGenerator: lambda tg: f"TextGenerator-{tg.process_id}" if tg else None
        }
    )


class TextGenActionEvent(BaseActionEvent):
    pass


class TextGenResponseEvent(BaseResponseEvent):
    data: TextResponse


class TextGenStepEvent(BaseStepEvent[TextGenInputEvent, TextGenActionEvent, TextGenResponseEvent]):
    pass
