from typing import Union, Literal, Optional, List

from pydantic import BaseModel, Field, ConfigDict

FinishReason = Union[str, Literal["stop", "length", "content_filter"]]


class TopLogprob(BaseModel):
    token: str
    bytes: Optional[List[int]] = Field(default=None)
    logprob: float


class LogProb(BaseModel):
    token: str
    bytes: Optional[List[int]] = Field(default=None)
    logprob: float
    top_logprobs: List[TopLogprob]


class TextChoiceChunk(BaseModel):
    index: int
    """The index of the response in the list of responses."""

    content: Optional[str] = Field(default=None)
    """The contents of the chunk."""

    finish_reason: Optional[FinishReason] = Field(default=None)
    """The reason the model stopped generating tokens."""

    role: Optional[str] = Field(default=None)
    """The role of the response. Only used by some services"""

    logprobs: Optional[List[LogProb]] = Field(default=None)
    """Log probability information for the response."""


class TextChoice(BaseModel):
    index: int
    """The index of the response in the list of responses."""

    content: Optional[str] = Field(default=None)
    """The response content."""

    finish_reason: Optional[FinishReason] = Field(default=None)
    """The reason the model stopped generating tokens."""

    role: Optional[str] = Field(default=None)
    """The role of the response. Only used by some services"""

    logprobs: Optional[List[LogProb]] = Field(default=None)
    """Log probability information for the response."""

    model_config = ConfigDict(
        extra='allow',
    )

    @classmethod
    def from_chunks(
            cls,
            chunks: List[TextChoiceChunk]
    ) -> 'TextChoice':
        if not chunks or len(chunks) == 0:
            raise ValueError("Cannot create an LLMResponse from an empty list of chunks.")

        index = chunks[0].index
        content = ""
        finish_reason = chunks[-1].finish_reason

        role = chunks[0].role
        logprobs = []

        for chunk in chunks:
            if chunk.index != index:
                raise ValueError("Cannot create an LLMResponse from LLMResponseChunks with different indices.")
            if chunk.content is not None:
                content += chunk.content
            if chunk.logprobs is not None:
                logprobs += chunk.logprobs

        return cls(
            index=index,
            content=content,
            finish_reason=finish_reason,
            role=role,
            logprobs=logprobs
        )
