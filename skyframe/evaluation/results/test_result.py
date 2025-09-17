from typing import List, Union, Any

from pydantic import Field

from .base_result import GradedResult
from .input_result import InputResult
from .assertion_result import AssertionResult


class TestResult(GradedResult):
    assertions: List[Any] = Field(default_factory=list)

    input_results: Union[InputResult, List[InputResult]]
    assertion_results: List[AssertionResult] = Field(default_factory=list)
    """Results of the individual assertions."""
