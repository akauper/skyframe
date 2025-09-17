import json
from typing import ClassVar

import jinja2
from devtools import debug

from skyframe import Message, StopwatchContext
from skyframe.evaluation.results.assertion_result import AssertionResult
from .base_model_graded_assertion import BaseModelGradedAssertion
from .prompts import DEFAULT_GRADING_PROMPT
from ..base_assertion import SingleInputAssertion


class LLMRubricAssertion(SingleInputAssertion, BaseModelGradedAssertion):
    """
    Checks if the LLM output matches given requirements,
    using a language model to grade the output based on the rubric.
    """

    type: ClassVar[str] = 'llm-rubric'

    async def _resolve_one(self, input: str) -> AssertionResult:
        self._raise_if_no_value()
        self._raise_if_list_value()

        async with StopwatchContext() as sw:
            environment = jinja2.Environment()
            template = environment.from_string('Output: {{ output }}\nRubric: {{ rubric }}')

            messages = [
                Message.from_system(
                    content=DEFAULT_GRADING_PROMPT
                ),
                Message.from_user(template.render(output=input, rubric=self.value))
            ]

            response = await self._get_model_response(messages)

        response_dict = json.loads(response.content)
        response_dict.update({
            'resolvable': self.type,
            'assertion': self,
            'expectation': f'Input {"does not meet" if self.inverted else "meets"} the rubric "{self.value}"',
            'token_usage': response.token_usage,
            'latency_ms': sw.elapsed_ms_int,
        })

        try:
            return AssertionResult.model_validate(response_dict)
        except Exception as e:
            debug(response_dict)
            raise e
