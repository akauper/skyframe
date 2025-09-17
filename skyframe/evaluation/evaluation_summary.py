from datetime import datetime
from typing import Optional
from uuid import uuid4
from .results.evaluation_result import EvaluationResult
from .resolvables.evaluation import Evaluation

from pydantic import BaseModel, Field


class EvaluationSummary(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    name: Optional[str] = Field(default=None)

    evaluation: Evaluation
    """The evaluation that was run."""

    evaluation_result: EvaluationResult
    """The result of the evaluation."""
