from typing import ClassVar, List, Optional, Union

from pydantic import Field

from skyframe.evaluation.results.assertion_result import AssertionResult
from skyframe.evaluation.results.input_result import InputResult
from ..base_assertion import MetaAssertion


class CostAssertion(MetaAssertion):
    """
    Check the perplexity of the model output.
    """

    type: ClassVar[str] = "cost"

    threshold: Optional[float] = Field(default=None)

    async def _resolve_meta(self, input_result: Union[InputResult, List[InputResult]]):
        if isinstance(input_result, list):
            raise ValueError(
                "Cost assertion expects a single input result, not a list."
            )

        real_threshold: Optional[float] = self.threshold
        if real_threshold is None:
            real_threshold = float(self.value) or None

        expectation = f"Cost {'>' if self.inverted else '<='} ${real_threshold:.6f}"

        if (
                not input_result
                or not input_result.text_response
                or not input_result.token_usage
                or not input_result.text_response.model
        ):
            return AssertionResult(
                resolvable=self,
                assertion=self,
                expectation=expectation,

                passed=True,
                score=1,
                reason="No valid input result",
            )

        cost = input_result.token_usage.total_cost

        passed = self._invert_if_needed(
            cost <= real_threshold if real_threshold is not None else True
        )

        return AssertionResult(
            resolvable=self,
            assertion=self,
            expectation=expectation,

            passed=passed,
            score=1 if passed else 0,
            reason="Assertion Passed"
            if passed
            else f"Cost is {'<=' if self.inverted else '>'} ${real_threshold:.6f}",
        )
