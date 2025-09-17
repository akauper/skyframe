from datetime import datetime
from typing import List, Optional

from pydantic import Field

from .base_result import GradedResult
from .test_summary import TestSummary


class EvaluationResult(GradedResult):
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    name: Optional[str] = Field(default=None)

    successful_tests: int = Field(default=0)
    """Number of successful tests."""

    failed_tests: int = Field(default=0)
    """Number of failed tests."""

    test_summaries: List[TestSummary] = Field(default_factory=list)

    # test_results: Dict[BaseInput, List[TestResult]]
    # test_results: Dict[int, List[TestResult]]
    # """ The results of the individual tests. Grouped by test index. """
