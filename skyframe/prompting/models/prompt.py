import re
from typing import Set

from pydantic import BaseModel, Field


class Prompt(BaseModel):
    template: str

    input_keys: Set[str] = Field(default_factory=set)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        template_str = kwargs.get('template', '')

        if re.fullmatch(r"[-a-zA-Z0-9_/]+", template_str):
            no_spaces = True
            # TODO: Load Files etc.

        self.input_keys = self._parse_template_variables(template_str)

    @staticmethod
    def _parse_template_variables(template_str: str) -> Set[str]:
        """Parse the format variables from a string."""
        pattern = r"\{([^}]+)\}"
        var_list = re.findall(pattern, template_str)
        return set(var_list)

    def format(self, **kwargs) -> str:
        return self.template.format(**kwargs)

    def __repr__(self):
        return f"Prompt(template={self.template[:50]}, input_keys={list(self.input_keys)})"
