from typing import Optional

from pydantic import BaseModel, Field

from skyframe.models.base import UIDMixin, CreatedAtMixin


class ModerationParameter(BaseModel):
    flagged: bool = Field(default=False)
    score: float = Field(default=0.0)

    def __add__(self, other: 'ModerationParameter'):
        if other is None:
            return self.model_copy() if self else None
        if self is None:
            return other.model_copy() if other else None
        return self.__class__(
            flagged=self.flagged or other.flagged,
            score=max(self.score, other.score)
        )


class ModerationResponse(UIDMixin, CreatedAtMixin):
    model: str
    """ The model used to generate this moderation result. """

    flagged: bool
    """ Whether the input was flagged to violate usage policies. """

    prompt_injection: Optional[ModerationParameter] = Field(default=None)
    """ Content that injects a prompt into the conversation. """

    harassment: Optional[ModerationParameter] = Field(default=None)
    """ Content that expresses, incites, or promotes harassing language towards any target. """

    harassment_threatening: Optional[ModerationParameter] = Field(default=None, alias="harassment/threatening")
    """ Harassment content that also includes violence or serious harm towards any target. """

    hate: Optional[ModerationParameter] = Field(default=None)
    """ Content that expresses, incites, or promotes hatred towards a group of people. """

    hate_threatening: Optional[ModerationParameter] = Field(default=None, alias="hate/threatening")
    """ Hate content that also includes violence or serious harm towards a group of people. """

    self_harm: Optional[ModerationParameter] = Field(default=None)
    """ Content that promotes, encourages, or depicts acts of self-harm, such as suicide, cutting, and eating disorders."""

    self_harm_instructions: Optional[ModerationParameter] = Field(default=None, alias="self-harm/instructions")
    """ Content that encourages performing acts of self-harm, such as suicide, cutting,
    and eating disorders, or that gives instructions or advice on how to commit such
    acts. """

    self_harm_intent: Optional[ModerationParameter] = Field(default=None, alias="self-harm/intent")
    """ Content where the speaker expresses that they are engaging or intend to engage
    in acts of self-harm, such as suicide, cutting, and eating disorders. """

    sexual: Optional[ModerationParameter] = Field(default=None)
    """ Content meant to arouse sexual excitement, such as the description of sexual
    activity, or that promotes sexual services (excluding sex education and
    wellness). """

    sexual_minors: Optional[ModerationParameter] = Field(default=None, alias="sexual/minors")
    """ Sexual content that includes an individual who is under 18 years old. """

    violence: Optional[ModerationParameter] = Field(default=None)
    """ Content that depicts death, violence, or physical injury. """

    violence_graphic: Optional[ModerationParameter] = Field(default=None, alias="violence/graphic")
    """ Content that depicts death, violence, or physical injury in graphic detail. """

    def __add__(self, other: 'ModerationResponse'):
        if other is None:
            return self

        if self.model != "" and other.model != "":
            model = f"{self.model} + {other.model}"
        elif self.model != "":
            model = self.model
        else:
            model = other.model

        return self.__class__(
            model=model,
            flagged=self.flagged or other.flagged,
            prompt_injection=ModerationParameter.__add__(self.prompt_injection, other.prompt_injection),
            harassment=ModerationParameter.__add__(self.harassment, other.harassment),
            harassment_threatening=ModerationParameter.__add__(self.harassment_threatening, other.harassment_threatening),
            hate=ModerationParameter.__add__(self.hate, other.hate),
            hate_threatening=ModerationParameter.__add__(self.hate_threatening, other.hate_threatening),
            self_harm=ModerationParameter.__add__(self.self_harm, other.self_harm),
            self_harm_instructions=ModerationParameter.__add__(self.self_harm_instructions, other.self_harm_instructions),
            self_harm_intent=ModerationParameter.__add__(self.self_harm_intent, other.self_harm_intent),
            sexual=ModerationParameter.__add__(self.sexual, other.sexual),
            sexual_minors=ModerationParameter.__add__(self.sexual_minors, other.sexual_minors),
            violence=ModerationParameter.__add__(self.violence, other.violence),
            violence_graphic=ModerationParameter.__add__(self.violence_graphic, other.violence_graphic)
        )

    def __iadd__(self, other: 'ModerationResponse'):
        return self.__add__(other)
