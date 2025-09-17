from typing import Optional, List, Dict

import numpy as np
from pydantic import BaseModel, Field


class SpeechToTextResponseChunk(BaseModel):
    """
    Represents a text response chunk from a speech-to-text model.

    This class is used is what Quiply converts all speech-to-text response chunks from different services into.
    """

    index: int
    """The index of this speech-to-text response chunk in the sequence of chunks."""

    text: Optional[str] = Field(default=None)
    """ The generated text chunk. """

    language: Optional[str] = Field(default=None)
    """ The language of the text. """

    language_probs: Optional[Dict[str, float]] = Field(default=None)
    """ The language probabilities of the text. """

    tokens: List[int] = Field(default_factory=list)

    is_final: bool = Field(default=False)
    """Whether this chunk is the final chunk in a streaming response."""


class SpeechToTextResponse(BaseModel):
    """
    Represents a text response from a speech-to-text model.

    This class is used is what Quiply converts all speech-to-text responses from different services into.
    """

    text: Optional[str] = Field(default=None)
    """ The generated text. """

    language: Optional[str] = Field(default=None)
    """ The language of the text. """

    language_probs: Optional[Dict[str, float]] = Field(default=None)
    """ The language probabilities of the text. """

    tokens: List[int] = Field(default_factory=list)

    avg_logprob: float = Field(default=np.nan)

    no_speech_prob: float = Field(default=np.nan)

    temperature: float = Field(default=np.nan)

    compression_ratio: float = Field(default=np.nan)

    @classmethod
    def from_chunks(
            cls,
            chunks: List[SpeechToTextResponseChunk]
    ) -> 'SpeechToTextResponse':
        """
        Combine a list of speech-to-text response chunks into a single speech-to-text response.
        """

        if not chunks or len(chunks) == 0:
            raise ValueError("Cannot create an SpeechToTextResponse from an empty list of chunks.")

        text = ''
        lang_count: Dict[str, int] = {}
        language_probs: Dict[str, float] = {}
        tokens = []

        for chunk in chunks:
            if chunk.text:
                text += chunk.text
            if chunk.language:
                lang_count.setdefault(chunk.language, 0)
                lang_count[chunk.language] += 1
            if chunk.language_probs:
                for lang, prob in chunk.language_probs.items():
                    language_probs.setdefault(lang, 0.0)
                    language_probs[lang] += prob
            if chunk.tokens:
                tokens.extend(chunk.tokens)

        language = None
        if len(lang_count) > 0:
            language = max(lang_count, key=lang_count.get)

        return cls(
            text=text,
            language=language,
            language_probs=language_probs if len(language_probs) > 0 else None,
            tokens=tokens
        )
