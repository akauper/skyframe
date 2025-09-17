from typing import ClassVar

from ..base_assertion import SingleInputAssertion
from skyframe.evaluation.results.assertion_result import AssertionResult


class EndsWithAssertion(SingleInputAssertion):
    type: ClassVar[str] = "ends-with"

    async def _resolve_one(self, result: str) -> AssertionResult:
        self._raise_if_no_value()
        self._raise_if_list_value()

        if self.case_sensitive:
            passed = self._invert_if_needed(result.lower().endswith(self.value.lower()))
        else:
            passed = self._invert_if_needed(result.endswith(self.value))

        return AssertionResult(
            resolvable=self,
            assertion=self,
            requirement=f'Input {"does not end with" if self.inverted else "ends with"} value "{self.value}"',

            passed=passed,
            score=1.0 if passed else 0.0,
            reason="Assertion Passed"
            if passed
            else f'Input {"ends with" if self.inverted else "does not end with"} "{result}"',
        )
