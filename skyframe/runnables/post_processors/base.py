from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Union

from skyframe.models import Message
from ..base import Runnable
from ..generators.text.models import TextResponse

TOutput = TypeVar("TOutput")
TInput = TypeVar("TInput", bound=Union[TextResponse, Message, str])


class BasePostProcessor(Runnable, Generic[TOutput], ABC):
    """
    Base class for parsing the output of a TextGenerator or Agent call.
    Post-processors are used to transform the output of a Generator call into a structured output.
    """

    @abstractmethod
    def get_generator_instructions_str(self) -> str:
        """Get the instructions for the generator on how it should format its response."""

    @abstractmethod
    async def run_async(self, generator_output: TInput) -> TOutput:
        """Parse the output of a Generator call."""

    def run(self, generator_output: TInput) -> TOutput:
        """Parse the output of a Generator call."""
