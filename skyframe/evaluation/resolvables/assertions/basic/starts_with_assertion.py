from typing import ClassVar

from ..base_assertion import SingleInputAssertion
from skyframe.evaluation.results.assertion_result import AssertionResult


class StartsWithAssertion(SingleInputAssertion):
    type: ClassVar[str] = "starts-with"

    async def _resolve_one(self, result: str) -> AssertionResult:
        self._raise_if_no_value()
        self._raise_if_list_value()

        if self.case_sensitive:
            passed = self._invert_if_needed(result.lower().startswith(self.value.lower()))
        else:
            passed = self._invert_if_needed(result.startswith(self.value))

        return AssertionResult(
            resolvable=self,
            assertion=self,
            expectation=f"Input {'does not start with' if self.inverted else 'starts with'} value '{self.value}'",

            passed=passed,
            score=1.0 if passed else 0.0,
            reason="Assertion Passed"
            if passed
            else f'Input {"starts with" if self.inverted else "does not start with"} "{result}"',
        )
