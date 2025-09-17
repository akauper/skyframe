from typing import ClassVar

from ..base_assertion import SingleInputAssertion
from skyframe.evaluation.results.assertion_result import AssertionResult


class ContainsAnyAssertion(SingleInputAssertion):
    type: ClassVar[str] = "contains-any"

    async def _resolve_one(self, result: str) -> AssertionResult:
        self._raise_if_no_value()
        self._raise_if_single_value()

        if self.case_sensitive:
            passed = self._invert_if_needed(any(val.lower() in [res.lower() for res in result] for val in self.value))
        else:
            passed = self._invert_if_needed(any(val in result for val in self.value))

        return AssertionResult(
            resolvable=self,
            assertion=self,
            expectation=f"Input {'does not contain' if self.inverted else 'contains'} any of [{self.value.join(', ')}]",

            passed=passed,
            score=1.0 if passed else 0.0,
            reason="Assertion Passed"
            if passed
            else f"Input {'contained' if self.inverted else 'did not contain'} one any of [{self.value.join(', ')}]",
        )
