import asyncio
from typing import Optional, List, Dict, Any, Tuple

from pydantic import Field, model_validator

from skyframe.utils import change_key, StopwatchContext
from .assertions import BaseAssertion
from .base_resolvable import BaseResolvable
from .eval_test import EvalTest
from .inputs import BaseInput
from ..results import GradedResult
from ..results.evaluation_result import EvaluationResult
from ..results.input_result import InputResult
from ..results.test_result import TestResult
from ..results.test_summary import TestSummary


class Evaluation(BaseResolvable[asyncio.Semaphore, EvaluationResult]):
    name: str
    """Name of the evaluation. If not provided, the name of the file or key will be used."""

    description: Optional[str] = Field(default=None)
    """Description of the evaluation."""

    inputs: List[BaseInput]
    """These inputs are used to generate the test prompts"""

    tests: List[EvalTest] = Field(default_factory=list)
    """These tests are run for each input"""

    async def resolve_async(self, semaphore: asyncio.Semaphore) -> EvaluationResult:
        test_summaries: List[TestSummary] = []
        for test in self.tests:
            test_summaries.append(TestSummary(
                passed=True,
                score=1,
                reason="No assertions to evaluate",

                test=test,
                test_results=[]
            ))

        async def process_input(test_input: BaseInput, test: EvalTest) -> Tuple[InputResult, TestResult]:
            async with semaphore:
                input_result = await test_input.resolve_async(test.vars)
                test_result = await test.resolve_async(input_result)
                return input_result, test_result

        async def process_test(test_index: int, test: EvalTest) -> None:
            test_summary = test_summaries[test_index]
            input_results: List[InputResult] = []

            test_tasks = [process_input(test_input, test) for test_input in self.inputs]

            for input_result, test_result in await asyncio.gather(*test_tasks):
                input_results.append(input_result)
                test_summary.test_results.append(test_result)

            async with semaphore:
                multi_input_result = await test.resolve_multi_input_async(input_results)
                test_summary.test_results.append(multi_input_result)

        tasks = [process_test(test_index, test) for test_index, test in enumerate(self.tests)]

        async with StopwatchContext() as sw:
            await asyncio.gather(*tasks)

        for summary in test_summaries:
            combined = GradedResult.combine(*summary.test_results)
            summary.passed = combined.passed
            summary.score = combined.score
            summary.reason = combined.reason

        successful_tests = sum(1 for summary in test_summaries if summary.passed)
        failed_tests = len(test_summaries) - successful_tests
        combined = GradedResult.combine(*test_summaries)

        failed_summaries = sum(1 for summary in test_summaries if not summary.passed)

        return EvaluationResult(
            resolvable=self,

            name=self.name,

            successful_tests=successful_tests,
            failed_tests=failed_tests,

            test_summaries=test_summaries,

            passed=combined.passed,
            score=combined.score,
            reason='' if combined.passed else f"{failed_summaries} tests failed",

            token_usage=combined.token_usage,
            latency_ms=sw.elapsed_ms_int
        )

    # async def resolve_async(self, semaphore: asyncio.Semaphore) -> EvaluationResult:
    #     test_results: Dict[int, List[TestResult]] = {}
    #
    #     async def process_input(test_input: BaseInput, test: EvalTest) -> Tuple[InputResult, TestResult]:
    #         async with semaphore:
    #             input_result = await test_input.resolve_async(test.vars)
    #             test_result = await test.resolve_async(input_result)
    #             return input_result, test_result
    #
    #     async def process_test(test_index: int, test: EvalTest) -> None:
    #         input_results: List[InputResult] = []
    #
    #         test_tasks = [process_input(test_input, test) for test_input in self.inputs]
    #
    #         for input_result, test_result in await asyncio.gather(*test_tasks):
    #             input_results.append(input_result)
    #             test_results.setdefault(test_index, []).append(test_result)
    #
    #         async with semaphore:
    #             multi_input_result = await test.resolve_multi_input_async(input_results)
    #             test_results[test_index].append(multi_input_result)
    #
    #     tasks = [process_test(test_index, test) for test_index, test in enumerate(self.tests)]
    #
    #     async with StopwatchContext() as sw:
    #         await asyncio.gather(*tasks)
    #
    #     flattened_test_results = [result for results in test_results.values() for result in results]
    #     successful_tests = sum(1 for result in flattened_test_results if result.passed)
    #     failed_tests = len(flattened_test_results) - successful_tests
    #     combined = GradedResult.combine(*flattened_test_results)
    #
    #     return EvaluationResult(
    #         resolvable=self,
    #
    #         name=self.name,
    #
    #         successful_tests=successful_tests,
    #         failed_tests=failed_tests,
    #
    #         test_results=test_results,
    #
    #         passed=combined.passed,
    #         score=combined.score,
    #         reason=combined.reason,
    #
    #         token_usage=combined.token_usage,
    #         latency_ms=sw.elapsed_ms_int
    #     )

    @model_validator(mode="before")
    @classmethod
    def transform_validation(cls, data: Dict[str, Any]):
        # Change alias keys to correct keys
        change_key(data, "test", "tests")
        change_key(data, "input", "inputs")
        change_key(data, "assert", "assertions")
        change_key(data, "assert_all", "assertions")

        # Inputs
        data["inputs"] = BaseInput.spread_data_dicts(data["inputs"])
        inputs = BaseInput.model_validate_subclasses(data["inputs"])
        data["inputs"] = inputs

        # Tests
        tests = EvalTest.model_validate_many(data["tests"])
        global_assertions = BaseAssertion.model_validate_subclasses(data["assertions"])
        for test in tests:
            test.assertions.extend(global_assertions)
        data["tests"] = tests

        return data
