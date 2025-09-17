import math
from typing import ClassVar, List, Optional, Union

from pydantic import Field

from ..base_assertion import MetaAssertion
from skyframe.evaluation.results.assertion_result import AssertionResult
from skyframe.evaluation.results.input_result import InputResult


class PerplexityScoreAssertion(MetaAssertion):
    """
    Check the perplexity of the model output.
    """

    type: ClassVar[str] = "perplexity-score"

    threshold: Optional[float] = Field(default=None)

    async def _resolve_meta(self, input_result: Union[InputResult, List[InputResult]]):
        if isinstance(input_result, list):
            raise ValueError(
                "Perplexity Score assertion expects a single input result, not a list."
            )

        if (
                not input_result
                or not input_result.text_response
                or not input_result.text_response.choice
                or not input_result.text_response.choice.logprobs
        ):
            return AssertionResult(
                resolvable=self,
                assertion=self,

                passed=True,
                score=1,
                reason="No valid input result",
            )

        real_threshold: Optional[float] = self.threshold
        if real_threshold is None:
            real_threshold = float(self.value) or None

        logprobs: List[float] = [lp.logprob for lp in input_result.text_response.choice.logprobs]

        avg = sum(logprobs) / len(logprobs)
        perplexity = math.exp(-avg)
        perplexity_norm = 1 / (1 + perplexity)

        passed = self._invert_if_needed(perplexity <= real_threshold if real_threshold is not None else True)

        return AssertionResult(
            resolvable=self,
            assertion=self,
            expectation=f"Perplexity Score {'>' if self.inverted else '<='} {real_threshold:.2f}",

            passed=passed,
            score=perplexity_norm,
            reason="Assertion Passed"
            if passed
            else f"Perplexity Score {'<=' if self.inverted else '>'} {real_threshold:.2f}",
        )
