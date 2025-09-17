from typing import Literal

from pydantic import BaseModel, Field


class ModerationGenerationParams(BaseModel):
    """
    Parameters for generating moderation from a service.
    """

    device: Literal['cpu', 'cuda'] = Field(default='cpu')
