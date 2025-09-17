from typing import Optional, Dict

from pydantic import Field

from .prompt import Prompt


class EvaluablePrompt(Prompt):
    name: str
    scenario: Optional[str] = Field(default=None)
    alternatives: Dict[str, str] = Field(default_factory=dict)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.scenario is None:
            if '.' not in self.name:
                self.scenario = self.name
            else:
                self.scenario = self.name.split('.')[-1]

    @property
    def default_prompt(self) -> Prompt:
        """Return the default prompt without evaluation context."""
        return Prompt(template=self.template)

    def get_prompt(self) -> Prompt:
        """Return the prompt to use for the current evaluation context."""

        from skyframe.settings import framework_settings

        if not framework_settings.evaluation.enabled:
            return self.default_prompt

        from skyframe.evaluation import EvaluationContext

        ctx = EvaluationContext.get_current_settings() or None

        # key = ctx.key if ctx is not None else framework_settings.evaluation.evaluation_prompt_key
        key = ctx.get('key') if ctx else None

        if not key or key not in self.alternatives:
            return self.default_prompt

        return Prompt(template=self.alternatives[key])

    def format(self, **kwargs) -> str:
        return self.get_prompt().format(**kwargs)

    def __repr__(self):
        return f"EvaluablePrompt(name={self.name}, scenario={self.scenario}, template={self.template[:50]}, input_keys={list(self.input_keys)})"
