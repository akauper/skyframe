from typing import ClassVar, Dict

from .base_input import BaseInput
from ...results.input_result import InputResult


class LiteralInput(BaseInput):
    type: ClassVar[str] = "literal"

    async def resolve_async(self, input: Dict[str, str]) -> InputResult:
        return InputResult(
            resolvable=self,

            raw_template=self.value,
            vars=input,
            rendered_template=self.value,
            value=str(self.value),
        )
