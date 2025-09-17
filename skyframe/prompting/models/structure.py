from typing import Any, Optional

from pydantic import BaseModel, ValidationError, Field, ConfigDict

from .evaluable_prompt import EvaluablePrompt


class EvaluablePromptContainer(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )

    def __getattr__(self, item: str) -> Any:
        if item in self.model_extra:
            try:
                return EvaluablePrompt.model_validate(self.model_extra[item])
            except ValidationError as e:
                return self.__class__.model_validate(self.model_extra[item])
        else:
            return super().__getattr__(item)


class PromptStructureBase(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )

    def __getattr__(self, item: str) -> Any:
        if item in self.model_extra:
            try:
                return EvaluablePrompt.model_validate(self.model_extra[item])
            except ValidationError as e:
                return EvaluablePromptContainer.model_validate(self.model_extra[item])
        else:
            return super().__getattr__(item)


class ScenarioCharacterPromptStructure(PromptStructureBase):
    instructions: Optional[EvaluablePrompt] = Field(default=None)
    role_and_behaviour: Optional[EvaluablePrompt] = Field(default=None)
    extra_information: Optional[EvaluablePrompt] = Field(default=None)


class ScenarioAnalysisPromptStructure(PromptStructureBase):
    skills_analysis: Optional[EvaluablePrompt] = Field(default=None)


class ScenarioPromptStructure(PromptStructureBase):
    character: ScenarioCharacterPromptStructure = Field(default_factory=ScenarioCharacterPromptStructure)
    analysis: ScenarioAnalysisPromptStructure = Field(default_factory=ScenarioAnalysisPromptStructure)

    description: Optional[EvaluablePrompt] = Field(default=None)


class CommonCharacterPromptStructure(PromptStructureBase):
    system_message_structure: Optional[EvaluablePrompt] = Field(default=None)
    common_instructions: Optional[EvaluablePrompt] = Field(default=None)
    personality: Optional[EvaluablePrompt] = Field(default=None)
    summarize_personality: Optional[EvaluablePrompt] = Field(default=None)


class CommonAnalysisPromptStructure(PromptStructureBase):
    analysis_structure: Optional[EvaluablePrompt] = Field(default=None)
    social_analysis_instructions: Optional[EvaluablePrompt] = Field(default=None)
    actor_feedback: Optional[EvaluablePrompt] = Field(default=None)


class PromptStructure(PromptStructureBase):
    character: CommonCharacterPromptStructure = Field(default_factory=CommonCharacterPromptStructure)
    mentor: CommonCharacterPromptStructure = Field(default_factory=CommonCharacterPromptStructure)
    analysis: CommonAnalysisPromptStructure = Field(default_factory=CommonAnalysisPromptStructure)

    scenario_complete: Optional[EvaluablePrompt] = Field(default=None)

    scenario_progress_structure: Optional[EvaluablePrompt] = Field(default=None)
    scenario_progress_instructions: Optional[EvaluablePrompt] = Field(default=None)
    scenario_progress_stages: Optional[EvaluablePrompt] = Field(default=None)

    scenario_assessment: Optional[EvaluablePrompt] = Field(default=None)
    agent_impression: Optional[EvaluablePrompt] = Field(default=None)

    conversation: ScenarioPromptStructure = Field(default_factory=ScenarioPromptStructure)
    debate: ScenarioPromptStructure = Field(default_factory=ScenarioPromptStructure)
    elevator_pitch: ScenarioPromptStructure = Field(default_factory=ScenarioPromptStructure)
    interview: ScenarioPromptStructure = Field(default_factory=ScenarioPromptStructure)
    speed_dating: ScenarioPromptStructure = Field(default_factory=ScenarioPromptStructure)
    pitch_to_investors: ScenarioPromptStructure = Field(default_factory=ScenarioPromptStructure)
    sell_me_this_pen: ScenarioPromptStructure = Field(default_factory=ScenarioPromptStructure)

    dating: ScenarioPromptStructure = Field(default_factory=ScenarioPromptStructure)
    personal: ScenarioPromptStructure = Field(default_factory=ScenarioPromptStructure)
