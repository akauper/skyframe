import re
from typing import List

from .base import BasePostProcessor, TInput
from skyframe.models.message import Message
from ..generators.text.models import TextResponse


class CommaSeperatedListPostProcessor(BasePostProcessor[str]):

    def get_generator_instructions_str(self) -> str:
        return (
            "Your response should be a list of comma separated values, "
            "eg: `foo, bar, baz`"
        )

    async def run_async(self, generator_output: TInput) -> List[str]:
        return self.run(generator_output)

    def run(self, generator_output: TInput) -> List[str]:
        if isinstance(generator_output, TextResponse):
            text = generator_output.content
        elif isinstance(generator_output, Message):
            text = generator_output.content
        else:
            text = generator_output

        return text.strip().split(", ")


class NumberedListPostProcessor(BasePostProcessor[str]):

    def get_generator_instructions_str(self) -> str:
        return (
            "Your response should be a numbered list with each item on a new line. "
            "For example: \n\n1. foo\n\n2. bar\n\n3. baz"
        )

    async def run_async(self, generator_output: TInput) -> List[str]:
        return self.run(generator_output)

    def run(self, generator_output: TInput) -> List[str]:
        pattern = r"\d+\.\s([^\n]+)"

        if isinstance(generator_output, TextResponse):
            text = generator_output.content
        elif isinstance(generator_output, Message):
            text = generator_output.content
        else:
            text = generator_output

        return re.findall(pattern, text)


class MarkdownListPostProcessor(BasePostProcessor[str]):

    def get_generator_instructions_str(self) -> str:
        return "Your response should be a markdown list, " "eg: `- foo\n- bar\n- baz`"

    async def run_async(self, generator_output: TInput) -> List[str]:
        return self.run(generator_output)

    def run(self, generator_output: TInput) -> List[str]:
        pattern = r"^\s*[-*]\s([^\n]+)$"

        if isinstance(generator_output, TextResponse):
            text = generator_output.content
        elif isinstance(generator_output, Message):
            text = generator_output.content
        else:
            text = generator_output

        return re.findall(pattern, text, re.MULTILINE)
