from typing import Union, List

from skyframe.models.message import Message

TextGenerationRequest = Union[
    Message,
    List[Message],
    str,
]
