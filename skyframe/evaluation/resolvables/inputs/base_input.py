from abc import ABC
from typing import Dict, Any, List

from pydantic import computed_field

from ...results.input_result import InputResult
from ..base_resolvable import BaseResolvable
from skyframe.utils.dict import change_key


class BaseInput(BaseResolvable[Dict[str, str], InputResult], ABC):
    @computed_field
    @property
    def input_type(self) -> str:
        return self.type

    value: str  # Template

    def tiny_str(self) -> str:
        return f"{self.type}: {self.value}"

    def __hash__(self):
        return hash((self.type, self.value))

    def __eq__(self, other):
        if isinstance(other, BaseInput):
            # Compare relevant attributes for equality
            return (
                    self.type == other.type
                    and self.value == other.value
            )
        return False

    @staticmethod
    def spread_data_dict(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        change_key(data, "prompts", "values")
        change_key(data, "prompt", "values")
        change_key(data, "value", "values")

        # Convert values to list
        if not isinstance(data["values"], list):
            data["values"] = [data["values"]]

        values = data["values"]
        del data["values"]

        spread_inputs: List[Dict[str, Any]] = []
        for value in values:
            new_input = data.copy()
            new_input["value"] = value
            spread_inputs.append(new_input)

        return spread_inputs

    @staticmethod
    def spread_data_dicts(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        spread_inputs: List[Dict[str, Any]] = []
        for input_dict in data:
            spread_inputs.extend(BaseInput.spread_data_dict(input_dict))
        return spread_inputs
