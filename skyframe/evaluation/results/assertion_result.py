from typing import Dict, Optional, Any

from pydantic import Field

from .base_result import GradedResult


class AssertionResult(GradedResult):
    assertion: Any
    """The assertion that generated the result."""

    expectation: str
    """The expectation for the assertion result."""

    named_scores: Dict[str, float] = Field(default_factory=dict)
    """Scores for named metrics."""

    comment: Optional[str] = Field(default=None)
    """A comment for the assertion result."""
