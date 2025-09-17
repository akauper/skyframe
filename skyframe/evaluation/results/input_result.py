from typing import Dict, Any, List, Optional

from pydantic import Field

from .base_result import BaseResult
from skyframe.runnables.generators.text.models.response import TextResponse


class InputResult(BaseResult):
    raw_template: str
    """ The template used to generate the input. """

    vars: Dict[str, str] = Field(default_factory=dict)
    """ The variables used in the template. """

    rendered_template: str
    """ The template after the variables have been filled in. """

    value: str
    """ The value of the result. Usually a response from an LLM. """

    steps: List[Any] = Field(default_factory=list)
    """ The steps taken to generate the result. """

    text_response: Optional[TextResponse] = Field(default=None)
    """ The TextResponse from the LLM (if applicable). """
