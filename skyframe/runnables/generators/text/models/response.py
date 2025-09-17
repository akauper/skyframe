from typing import List, Optional, Dict

from pydantic import BaseModel, Field

from skyframe.models.token_usage import TokenUsage
from .choice import TextChoice, TextChoiceChunk


class TextResponseChunk(BaseModel):
    """
    Represents a text response chunk from a text generation model.

    This class is what Quiply converts all text response chunks from different services into.
    """

    id: str
    """A unique identifier for the completion. Each chunk has the same ID."""

    index: int
    """The index of the chunk in the stream of chunks."""

    choices: List[TextChoiceChunk] = Field(default_factory=list)
    """A list of choice chunks from the model."""

    created_at: int
    """The Unix timestamp (in seconds) of when the completion was created. Each chunk has the same timestamp."""

    model: Optional[str] = Field(default=None)
    """The model used to generate the completion."""

    system_fingerprint: Optional[str] = Field(default=None)
    """OpenAI only uses this internally. Check their docs for more info."""

    is_final: bool = Field(default=False)
    """ Whether or not this is the final chunk in the stream of chunks. """

    @property
    def response(self) -> Optional[TextChoiceChunk]:
        """ Returns the first choice from the list of choices. (Usually the only choice.) """
        if not self.choices or len(self.choices) == 0:
            return None
        return self.choices[0]

    @property
    def content(self) -> Optional[str]:
        """ Returns the content from the first choice from the list of choices. (Usually the only choice.) """
        if self.response is None:
            return None
        return self.response.content


class TextResponse(BaseModel):
    """
    Represents a text response from a text generation model.

    This class is what Quiply converts all text responses from different LLM services into.
    """

    id: str
    """A unique identifier for the completion."""

    choices: List[TextChoice] = Field(default_factory=list)
    """A list of choices from the model."""

    created_at: int
    """The Unix timestamp (in seconds) of when the completion was created."""

    model: Optional[str] = Field(default=None)
    """The model used to generate the completion."""

    system_fingerprint: Optional[str] = Field(default=None)
    """OpenAI only uses this internally. Check their docs for more info."""

    token_usage: Optional[TokenUsage] = Field(default=None)
    """Usage information for the completion. Token counts, etc."""

    @property
    def choice(self) -> Optional[TextChoice]:
        """Returns the first choice from the completion. (Usually the only choice.)"""
        if not self.choices or len(self.choices) == 0:
            return None
        return self.choices[0]

    @property
    def content(self) -> Optional[str]:
        """Returns the content from the first choice from the completion. (Usually the only choice.)"""
        if self.choice is None:
            return None
        return self.choice.content

    @classmethod
    def from_chunks(
            cls,
            chunks: List[TextResponseChunk]
    ) -> "TextResponse":
        if not chunks or len(chunks) == 0:
            raise ValueError("Cannot create a Completion from an empty list of chunks.")

        id = chunks[0].id
        choices = []
        created_at = chunks[-1].created_at
        model = chunks[0].model
        system_fingerprint = chunks[0].system_fingerprint
        usage = None

        # First we need to group the chunks by their index.
        indexed_response_chunks: Dict[int, List[TextChoiceChunk]] = {}
        for chunk in chunks:
            if chunk.is_final:
                continue
            for response_chunk in chunk.choices:
                indexed_response_chunks.setdefault(response_chunk.index, []).append(response_chunk)

        # Now we can create the responses.
        for index, response_chunks in indexed_response_chunks.items():
            choices.append(TextChoice.from_chunks(response_chunks))

        return cls(
            id=id,
            choices=choices,
            created_at=created_at,
            model=model,
            system_fingerprint=system_fingerprint,
            token_usage=usage
        )
