from typing import Dict, Any, ClassVar

import jinja2
from pydantic import Field

from skyframe import TextGenerator, RunnableParams, TextGenerationParams, StopwatchContext
from skyframe.evaluation.callback import EvaluationCallback
from skyframe.evaluation.results.input_result import InputResult
from ..base_input import BaseInput


class TextGeneratorInput(BaseInput):
    type: ClassVar[str] = "text-generator"
    provider: str = Field(default="openai:gpt-3.5-turbo")
    params: Dict[str, Any] = Field(default_factory=dict)

    async def resolve_async(self, input: Dict[str, str]) -> InputResult:
        callback = EvaluationCallback(runnable_type=TextGenerator)

        generation_params: TextGenerationParams = TextGenerationParams(**self.params)
        runnable_params: RunnableParams = RunnableParams(callbacks=[callback])

        text_generator = TextGenerator(
            generation_params=generation_params,
            runnable_params=runnable_params,
        )

        rendered_template = self._render_template(self.value, input)

        async with StopwatchContext() as sw:
            response = await text_generator.run_async(rendered_template)

        return InputResult(
            resolvable=self,

            raw_template=self.value,
            vars=input,
            rendered_template=rendered_template,
            value=response.content,

            steps=callback.steps,
            text_response=response,

            latency_ms=sw.elapsed_ms_int,
            token_usage=response.token_usage,
        )

    @staticmethod
    def _render_template(value: str, vars: Dict[str, str]) -> str:
        environment = jinja2.Environment()
        template = environment.from_string(value)
        return template.render(**vars)
