from typing import ClassVar

from pydantic import Field, ValidationError

from skyframe.utils import StopwatchContext
from skyframe.runnables.generators.embeddings import (
    EmbeddingsGenerationParams,
    EmbeddingsGenerator,
)
from .base_model_graded_assertion import BaseModelGradedAssertion
from ..base_assertion import SingleInputAssertion
from skyframe.evaluation.results.assertion_result import AssertionResult


class SimilarAssertion(SingleInputAssertion, BaseModelGradedAssertion):
    """
    Checks if the LLM output matches given requirements,
    using a language model to grade the output based on the rubric.
    """

    type: ClassVar[str] = "similar"

    threshold: float = Field(default=0.5)

    async def _resolve_one(self, result: str) -> AssertionResult:
        self._raise_if_no_value()
        self._raise_if_list_value()

        try:
            if self.params:
                generation_params = EmbeddingsGenerationParams.model_validate(self.params)
            else:
                generation_params = EmbeddingsGenerationParams()
        except ValidationError as e:
            print(f"Error validating embeddings generation params: {e}")
            generation_params = EmbeddingsGenerationParams()

        embeddings_generator = EmbeddingsGenerator(generation_params=generation_params)

        async with StopwatchContext() as sw:
            response = await embeddings_generator.run_async([self.value, result])
            similarity = response.compare_similarity()

        passed = self._invert_if_needed(similarity >= self.threshold)

        return AssertionResult(
            resolvable=self,
            assertion=self,
            expectation=f'Input {"is not similar to" if self.inverted else "is similar to"} value "{self.value}"',

            passed=passed,
            score=1 - similarity if self.inverted else similarity,
            reason="Assertion Passed"
            if passed
            else f"Similarity: {similarity:.2f} < {self.threshold:.2f}",

            token_usage=response.token_usage,
            latency_ms=sw.elapsed_ms_int,
        )
