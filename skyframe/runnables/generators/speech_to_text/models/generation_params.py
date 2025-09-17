from typing import Optional, Union, List, Iterable, Literal

from pydantic import BaseModel, Field


class SpeechToTextGenerationParams(BaseModel):
    """
    Parameters for generating text from an STT Service.
    """

    model: str = Field(default="base")
    """ The model ID to use for the generation. """

    device: Literal['cuda', 'cpu'] = Field(default='cpu')
    """ The device to run the model on. """

    task: str = Field(default='transcribe')
    """ Whether to perform X->X "transcribe" or X->English "translate" """

    language: Optional[str] = Field(default='en')
    """ language that the audio is in; uses detected language if None """

    temperature: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)
    """ The temperature of the generation. """

    max_tokens: Optional[int] = Field(default=None)
    """ maximum number of tokens to sample"""

    best_of: Optional[int] = Field(default=None)
    """ number of independent sample trajectories, if t > 0 """

    beam_size: Optional[int] = Field(default=None)
    """ number of beams in beam search, if t == 0 """

    patience: Optional[int] = Field(default=None)
    """ patience in beam search (arxiv:2204.05424) """

    length_penalty: Optional[float] = Field(default=None)
    """ "alpha" in Google NMT, or None for length norm, when ranking generations
    to select which to return among the beams or best-of-N samples"""

    prompt: Optional[Union[str, List[int]]] = Field(default=None)
    """ for the previous context. text or tokens to feed as the prompt or the prefix; for more info:
    https://github.com/openai/whisper/discussions/117#discussioncomment-3727051 """

    prefix: Optional[Union[str, List[int]]] = Field(default=None)
    """ to prefix the current context."""

    suppress_tokens: Optional[Union[str, Iterable[int]]] = Field(default="-1")
    """ list of tokens ids (or comma-separated token ids) to suppress
    "-1" will suppress a set of symbols as defined in `tokenizer.non_speech_tokens()` """

    suppress_blank: bool = Field(default=True)
    """ this will suppress blank outputs """

    without_timestamps: bool = Field(default=False)
    """ use <|notimestamps|> to sample text tokens only """

    max_initial_timestamp: Optional[float] = Field(default=1.0)
