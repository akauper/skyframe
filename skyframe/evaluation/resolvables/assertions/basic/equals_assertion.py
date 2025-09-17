from typing import ClassVar

from ..base_assertion import SingleInputAssertion
from skyframe.evaluation.results.assertion_result import AssertionResult


class EqualsAssertion(SingleInputAssertion):
    type: ClassVar[str] = "equals"

    async def _resolve_one(self, result: str) -> AssertionResult:
        self._raise_if_no_value()
        self._raise_if_list_value()

        if self.case_sensitive:
            passed = self._invert_if_needed(self.value.lower() == result.lower())
        else:
            passed = self._invert_if_needed(self.value == result)

        return AssertionResult(
            resolvable=self,
            assertion=self,
            expectation=f'Input {"does not equal" if self.inverted else "equals"} value "{self.value}"',

            passed=passed,
            score=1.0 if passed else 0.0,
            reason="Assertion Passed"
            if passed
            else f'Input {"equals" if self.inverted else "does not equal"} "{self.value}"',
        )
