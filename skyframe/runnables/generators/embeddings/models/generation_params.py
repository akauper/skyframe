from typing import Literal, Union, Optional

from pydantic import Field

from skyframe.models.base import BaseParams

OpenAiModelType = Union[
    str,
    Literal[
        "text-embedding-3-small",
        "text-embedding-3-large",
        "text-embedding-ada-002"
    ]
]

EncodingFormat = Literal['float', 'base64']


class EmbeddingsGenerationParams(BaseParams):
    model: Union[OpenAiModelType] = Field(default="text-embedding-3-small")
    """ The name of the LLM model to use for generation. """

    encoding_format: Optional[EncodingFormat] = Field(default=None)
    """ The format to return the embeddings in. Can be either float or base64. """

    dimensions: Optional[int] = Field(default=None, ge=1)
    """ The number of dimensions the resulting output embeddings should have.
    Only supported in text-embedding-3 and later models. """

    user: Optional[str] = Field(default=None)
    """ A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse. """
