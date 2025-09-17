from typing import ClassVar

from ..base_assertion import SingleInputAssertion
from skyframe.evaluation.results.assertion_result import AssertionResult


class ContainsAllAssertion(SingleInputAssertion):
    """ Assertion that checks if the input contains all the expected values. """
    type: ClassVar[str] = "contains-all"

    async def _resolve_one(self, result: str) -> AssertionResult:
        self._raise_if_no_value()
        self._raise_if_single_value()

        if self.case_sensitive:
            passed = self._invert_if_needed(all(val.lower() in [res.lower() for res in result] for val in self.value))
        else:
            passed = self._invert_if_needed(all(val in result for val in self.value))

        return AssertionResult(
            resolvable=self,
            assertion=self,
            expectation=f"Input {'does not' if self.inverted else ''} contain all of [{self.value.join(', ')}]",

            passed=passed,
            score=1.0 if passed else 0.0,
            reason="Assertion Passed"
            if passed
            else f'Input {"contained" if self.inverted else "did not contain"} all of [{self.value.join(", ")}]',
        )
