from typing import List, Any, Dict, Optional, Union

from pydantic import Field, model_validator

from skyframe.models import TokenUsage
from skyframe.utils import StopwatchContext
from skyframe.utils import change_key
from .assertions import *
from .base_resolvable import BaseResolvable
from ..results.input_result import InputResult
from ..results.test_result import TestResult


class EvalTest(BaseResolvable[InputResult, TestResult]):
    name: Optional[str] = Field(default=None)
    """Name of the test. If not provided, the name of the file or key will be used."""

    description: Optional[str] = Field(default=None)
    """Description of the test"""

    vars: Dict[str, str] = Field(default_factory=dict)
    """A dictionary of Key-value pairs to substitute in the prompt."""

    assertions: List[BaseAssertion] = Field(default_factory=list)
    """List of automatic checks to run on the LLM output (EvalInputResult)."""

    threshold: Optional[float] = Field(default=None)
    """Test will fail if the combined weighted score of all assertions is less than this number"""

    async def _resolve_async(
            self,
            input: Union[InputResult, List[InputResult]],
            assertions: List[BaseAssertion]
    ) -> TestResult:
        if not assertions or len(assertions) == 0:
            return TestResult(
                resolvable=self,
                assertions=assertions,
                input_results=input,

                passed=True,
                score=1.0,
                reason="No assertions to evaluate",
            )

        total_score = 0
        total_weight = 0
        all_pass = True
        failed_reason = ""
        assertion_results = []
        named_scores = {}
        token_usage = TokenUsage()
        input_latency_ms = 0

        # Add token usage from input
        if isinstance(input, list):
            for i in input:
                if i.token_usage is not None:
                    token_usage += i.token_usage
        elif input.token_usage is not None:
            token_usage += input.token_usage

        # Add elapsed time from input
        if isinstance(input, list):
            input_latency_ms += sum([i.latency_ms for i in input if i.latency_ms is not None])
        elif input.latency_ms is not None:
            input_latency_ms += input.latency_ms

        async with StopwatchContext() as sw:
            for assertion in assertions:
                assertion_result = await assertion.resolve_async(input)
                assertion_results.append(assertion_result)

                total_weight += assertion.weight
                total_score += assertion_result.score * assertion.weight

                if assertion.metric is not None:
                    named_scores.setdefault(assertion.metric, 0)
                    named_scores[assertion.metric] += assertion_result.score

                if assertion_result.token_usage is not None:
                    token_usage += assertion_result.token_usage

                if not assertion_result.passed:
                    all_pass = False
                    failed_reason = assertion_result.reason

        final_score = (total_score / total_weight) if total_weight > 0 else 0
        final_reason = "All assertions passed" if all_pass else failed_reason
        if self.threshold is not None:
            all_pass = final_score >= self.threshold
            if all_pass:
                final_reason = f"Aggregate score of {final_score} >= threshold of {self.threshold}"
            else:
                final_reason = f"Aggregate score of {final_score} < threshold of {self.threshold}"

        return TestResult(
            resolvable=self,

            assertions=assertions,

            input_results=input,
            assertion_results=assertion_results,

            passed=all_pass,
            score=final_score,
            reason=final_reason,

            token_usage=token_usage,
            latency_ms=sw.elapsed_ms_int + input_latency_ms,
        )

    async def resolve_async(self, input: InputResult) -> TestResult:
        return await self._resolve_async(input, self.single_input_assertions + self.meta_assertions)

    async def resolve_multi_input_async(self, inputs: List[InputResult]) -> TestResult:
        return await self._resolve_async(inputs, self.multi_input_assertions)

    @property
    def single_input_assertions(self) -> List[SingleInputAssertion]:
        ret = []
        for assertion in self.assertions:
            if isinstance(assertion, SingleInputAssertion):
                ret.append(assertion)
        return ret
        # return [a for a in self.assertions if not a.type.startswith("select-")]

    @property
    def multi_input_assertions(self) -> List[MultiInputAssertion]:
        ret = []
        for assertion in self.assertions:
            if isinstance(assertion, MultiInputAssertion):
                ret.append(assertion)
        return ret

        # return [a for a in self.assertions if a.type.startswith("select-")]

    @property
    def meta_assertions(self) -> List[MetaAssertion]:
        ret = []
        for assertion in self.assertions:
            if isinstance(assertion, MetaAssertion):
                ret.append(assertion)
        return ret

        # return [a for a in self.assertions if a.type.startswith("meta-")]

    def tiny_str(self) -> str:
        return f"""{self.name}:
description: {self.description}
assertions: {[assertion.tiny_str() for assertion in self.assertions]}
threshold: {self.threshold}"""

    @model_validator(mode="before")
    @classmethod
    def transform_validation(cls, data: Dict[str, Any]):
        change_key(data, "var", "vars")
        change_key(data, "vars_dict", "vars")

        change_key(data, "assert", "assertions")
        data["assertions"] = BaseAssertion.model_validate_subclasses(data["assertions"])
        return data

    @classmethod
    def model_validate_many(cls, tests: List[Dict[str, Any]]) -> List["EvalTest"]:
        return [cls.model_validate(test) for test in tests]
