from typing import Dict, Callable, Union, Any

from skyframe.models.message.base import Message
from .prompt import Prompt


class PromptMessage(Message):
    prompt: Prompt
    input_variables: Dict[str, Union[str, Callable[..., str]]]

    @property
    def content(self) -> str:
        vals: Dict[str, Any] = {}
        for k, v in self.input_variables.items():
            if isinstance(v, Callable):
                vals[k] = v()
            else:
                vals[k] = v
        return self.prompt.format(**vals)
