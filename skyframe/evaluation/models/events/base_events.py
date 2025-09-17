from abc import ABC
from typing import Any, Optional, TypeVar, Generic
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class BaseInputEvent(BaseModel, ABC):
    data: Optional[Any] = Field(default=None)


class BaseActionEvent(BaseModel, ABC):
    data: Optional[Any] = Field(default=None)


class BaseResponseEvent(BaseModel, ABC):
    data: Optional[Any] = Field(default=None)


TInputEvent = TypeVar('TInputEvent', bound=BaseInputEvent)
TActionEvent = TypeVar('TActionEvent', bound=BaseActionEvent)
TResponseEvent = TypeVar('TResponseEvent', bound=BaseResponseEvent)


class BaseStepEvent(BaseModel, Generic[TInputEvent, TActionEvent, TResponseEvent]):
    run_id: UUID
    parent_run_id: Optional[UUID] = Field(default=None)

    input: Optional[TInputEvent] = Field(default=None)
    actions: Optional[TActionEvent] = Field(default=None)
    response: Optional[TResponseEvent] = Field(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)


TStepEvent = TypeVar('TStepEvent', bound=BaseStepEvent)
