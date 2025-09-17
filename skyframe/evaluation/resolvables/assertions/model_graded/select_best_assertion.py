from typing import List, ClassVar

import jinja2

from skyframe.models import Message
from skyframe.utils import StopwatchContext
from .base_model_graded_assertion import BaseModelGradedAssertion
from .prompts import SELECT_BEST_PROMPT
from ..base_assertion import MultiInputAssertion
from skyframe.evaluation.results.assertion_result import AssertionResult


class SelectBestAssertion(MultiInputAssertion, BaseModelGradedAssertion):
    type: ClassVar[str] = 'select-best'

    async def _resolve_many(self, inputs: List[str]) -> AssertionResult:
        self._raise_if_no_value()
        self._raise_if_list_value()

        async with StopwatchContext() as sw:
            environment = jinja2.Environment()
            criteria = self.value

            template = environment.from_string(SELECT_BEST_PROMPT)
            message = Message.from_system(content=template.render(criteria=criteria, outputs=inputs))

            response = await self._get_model_response(message)

        return AssertionResult(
            resolvable=self,
            assertion=self,
            expectation=f'The input that is {"not " if self.inverted else ""}the best according to the criteria "{self.value}"',

            passed=True,
            score=1.0,
            reason=f'The best input index is {response.content}',

            token_usage=response.token_usage,
            latency_ms=sw.elapsed_ms_int,
        )
