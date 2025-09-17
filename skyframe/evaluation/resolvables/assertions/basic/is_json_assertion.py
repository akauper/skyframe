from typing import ClassVar

from ..base_assertion import SingleInputAssertion
from skyframe.evaluation.results.assertion_result import AssertionResult


class IsJsonAssertion(SingleInputAssertion):
    type: ClassVar[str] = "is-json"

    async def _resolve_one(self, result: str) -> AssertionResult:
        self._raise_if_no_value()
        self._raise_if_list_value()

        import json
        error = ''
        try:
            json.loads(result)
            passed = self._invert_if_needed(True)
        except json.JSONDecodeError as e:
            error = e.msg
            passed = self._invert_if_needed(False)

        return AssertionResult(
            resolvable=self,
            assertion=self,
            expectation=f"Input {'is not' if self.inverted else 'is'} valid JSON",

            passed=passed,
            score=1.0 if passed else 0.0,
            reason="Assertion Passed"
            if passed
            else f'Input JSON {"does" if self.inverted else "does not"} conform to the provided schema. Errors: "{error}"',
        )
