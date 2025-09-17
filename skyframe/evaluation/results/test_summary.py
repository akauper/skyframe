from typing import List, Any

from pydantic import Field

from .base_result import GradedResult
from .test_result import TestResult


class TestSummary(GradedResult):
    test: Any
    """ The tests that were run. """

    test_results: List[TestResult] = Field(default_factory=list)
    """ The results of the individual tests. """
