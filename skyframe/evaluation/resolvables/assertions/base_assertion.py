from abc import ABC, abstractmethod
from typing import Optional, List, TypeAlias, Union

from pydantic import Field, computed_field

from ..base_resolvable import BaseResolvable
from ...results.input_result import InputResult
from ...results.assertion_result import AssertionResult


AssertionInputTypes: TypeAlias = Union[str, List[str], InputResult, List[InputResult]]


class BaseAssertion(BaseResolvable[AssertionInputTypes, AssertionResult], ABC):
    """Base class for all evaluation assertions."""

    @computed_field
    @property
    def assertion_type(self) -> str:
        return self.__class__.type

    value: Optional[Union[str, List[str]]] = Field(default=None)
    """The expected value for the assertion."""

    inverted: bool = Field(default=False)
    """If true, the assertion will pass if the condition is not met."""

    case_sensitive: bool = Field(default=False)
    """If true, the value assessment of the assertion will be case sensitive."""

    weight: float = Field(default=1.0)
    """The weight of the assertion in the final score."""

    metric: Optional[str] = Field(default=None)
    """A metric label for the assertion."""

    def tiny_str(self) -> str:
        return f"{self.type}: {self.value}"

    def _invert_if_needed(self, result: bool) -> bool:
        return not result if self.inverted else result

    def _raise_if_no_value(self):
        if self.value is None:
            raise ValueError(f"Assertion {self.type} expects a value.")

    def _raise_if_list_value(self):
        if isinstance(self.value, list):
            raise ValueError(
                f"Assertion {self.type} expects a single value, not a list."
            )

    def _raise_if_single_value(self):
        if not isinstance(self.value, list):
            raise ValueError(
                f"Assertion {self.type} expects a list of values, not a single value."
            )


class SingleInputAssertion(BaseAssertion, ABC):
    """Base class for assertions that require a single input to evaluate."""

    @abstractmethod
    async def _resolve_one(self, input: str) -> AssertionResult:
        pass

    async def resolve_async(self, input: AssertionInputTypes) -> AssertionResult:
        if isinstance(input, list):
            raise ValueError("SingleInputEvalAssertion expects a single input.")

        assertion_result = await self._resolve_one(
            input if isinstance(input, str) else input.value
        )

        return assertion_result


class MultiInputAssertion(BaseAssertion, ABC):
    """Base class for assertions that require multiple inputs to evaluate."""

    @abstractmethod
    async def _resolve_many(self, inputs: List[str]) -> AssertionResult:
        pass

    async def resolve_async(self, input: AssertionInputTypes) -> AssertionResult:
        if isinstance(input, list):
            str_input = [
                item if isinstance(item, str) else item.value for item in input
            ]
            return await self._resolve_many(str_input)
        else:
            raise ValueError("MultiInputEvalAssertion expects a list of inputs.")


class MetaAssertion(BaseAssertion, ABC):
    """Base class for assertions that assert on the evaluation pipeline."""

    @abstractmethod
    async def _resolve_meta(self, input: Union[InputResult, List[InputResult]]) -> AssertionResult:
        pass

    async def resolve_async(self, input: AssertionInputTypes) -> AssertionResult:
        return await self._resolve_meta(input)
