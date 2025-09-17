from typing import Optional

from pydantic import Field, ConfigDict

from .base_events import BaseInputEvent, BaseActionEvent, BaseResponseEvent, BaseStepEvent
from skyframe.models import Message
from skyframe.runnables.agents import Agent
from skyframe.runnables.agents.tool import Tool


class AgentInputEvent(BaseInputEvent):
    data: Message
    agent: Optional[Agent] = Field(default=None)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            Agent: lambda a: a.id if a else None
        }
    )

    # @field_serializer('agent', when_used='json')
    # def serialize_agent(self, agent: Agent, _info):
    #     return agent.id if agent else None


class AgentActionEvent(BaseActionEvent):
    used_tool: bool = Field(default=False)
    tool: Optional[Tool] = Field(default=None)


class AgentResponseEvent(BaseResponseEvent):
    data: Message


class AgentStepEvent(BaseStepEvent[AgentInputEvent, AgentActionEvent, AgentResponseEvent]):
    pass
