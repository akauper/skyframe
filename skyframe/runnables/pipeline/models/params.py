from pydantic import BaseModel, Field


class PipelineParams(BaseModel):
    verbose: bool = Field(default=False)
