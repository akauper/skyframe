from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict
from typing_extensions import TypedDict

from .params import RunnableParams


class RunInfo(BaseModel):
    process_id: Optional[str] = Field(default=None)
    run_id: UUID = Field(default_factory=uuid4)
    parent_run_id: Optional[UUID] = Field(default=None)
    runnable_params: RunnableParams = Field(default_factory=RunnableParams)

    model_config = ConfigDict(extra='forbid')


class RunContext(TypedDict, total=False):
    info: RunInfo

# class RunInfo(BaseModel):
#     process_id: Optional[str] = Field(default=None)
#     run_id: str
#     parent_run_id: Optional[str] = Field(default=None)
#     runnable_params: RunnableParams
