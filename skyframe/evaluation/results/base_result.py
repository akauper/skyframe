from abc import ABC
from typing import TypeVar, Optional, Any
from uuid import uuid4

from pydantic import BaseModel, Field, AliasChoices

from skyframe.models import TokenUsage


class BaseResult(BaseModel, ABC):
    id: str = Field(default_factory=lambda: str(uuid4()))

    resolvable: Optional[Any] = Field(default=None, exclude=True)

    latency_ms: int = Field(default=0, ge=0)
    token_usage: Optional[TokenUsage] = Field(default=None)


class GradedResult(BaseResult, ABC):
    passed: bool = Field(validation_alias=AliasChoices("passed", "pass"))
    score: float = Field(ge=0, le=1)
    reason: str

    @classmethod
    def combine(cls, *results: 'GradedResult') -> 'GradedResult':
        total_score = 0
        all_passed = True
        failed_reason = ""
        token_usage = TokenUsage()
        latency_ms = 0

        for result in results:
            total_score += result.score

            if result.token_usage is not None:
                token_usage += result.token_usage

            if result.latency_ms is not None:
                latency_ms += result.latency_ms

            if not result.passed:
                all_passed = False
                failed_reason = result.reason

        final_score = (total_score / len(results)) if len(results) > 0 else 0
        final_reason = "All tests passed" if all_passed else failed_reason

        return cls(
            passed=all_passed,
            score=final_score,
            reason=final_reason,
            token_usage=token_usage
        )


TResult = TypeVar("TResult", bound=BaseResult)
TGradedResult = TypeVar("TGradedResult", bound=GradedResult)
