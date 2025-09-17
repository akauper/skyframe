from pydantic import BaseModel, Field


class EvaluatorOptions(BaseModel):
    max_concurrent_requests: int = Field(default=0)
    """Maximum number of concurrent requests to make to the LLM. If 0, all requests are made at once."""

    repeat: int = Field(default=1)
    """Number of times to repeat each test."""

    delay_ms: int = Field(default=0, ge=0)
    """Delay in milliseconds between API calls to LLMs. If None, no delay is added."""
