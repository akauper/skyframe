from typing import ClassVar

from ..base_assertion import SingleInputAssertion
from skyframe.evaluation.results.assertion_result import AssertionResult


class ContainsAssertion(SingleInputAssertion):
    type: ClassVar[str] = "contains"

    async def _resolve_one(self, result: str) -> AssertionResult:
        self._raise_if_no_value()
        self._raise_if_list_value()

        if self.case_sensitive:
            passed = self._invert_if_needed(self.value.lower() in result.lower())
        else:
            passed = self._invert_if_needed(self.value in result)

        return AssertionResult(
            resolvable=self,
            assertion=self,
            expectation=f"Input {'does not contain' if self.inverted else 'contains'} value '{self.value}'",

            passed=passed,
            score=1.0 if passed else 0.0,
            reason="Assertion Passed"
            if passed
            else f'Input {"contained" if self.inverted else "did not contain"} "{self.value}"',
        )
