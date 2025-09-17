from abc import ABC
from typing import Dict, Any, Optional

from pydantic import Field, ValidationError

from skyframe import TextGenerator, TextResponse, TextGenerationRequest, TextGenerationParams
from ..base_assertion import BaseAssertion


class BaseModelGradedAssertion(BaseAssertion, ABC):
    """ Base class for assertions that require a language model to grade. """

    provider: str = Field(default="openai:gpt-3.5-turbo")
    params: Optional[Dict[str, Any]] = Field(default=None)

    async def _get_model_response(self, request: TextGenerationRequest) -> TextResponse:
        try:
            if self.params:
                generation_params = TextGenerationParams.model_validate(self.params)
            else:
                generation_params = TextGenerationParams()
        except ValidationError as e:
            print(f"Error validating text generation params: {e}")
            generation_params = TextGenerationParams()

        text_generator: TextGenerator = TextGenerator(generation_params=generation_params)
        response = await text_generator.run_async(request)
        return response
