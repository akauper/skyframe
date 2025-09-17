from pydantic import field_validator

from ..base import Runnable


class Tool(Runnable):
    """
    A tool used by an agent to perform an action.

    A name and a description are required. The name should be short and is used to identify the tool. The description
    should be a short sentence describing the tool's purpose. The agent uses the description to decide whether to use
    the tool, so it should be clear and concise.
    """

    name: str
    description: str

    @field_validator('name')
    @classmethod
    def check_name_is_valid(cls, v: str) -> str:
        is_alphanumeric = v.replace('_', '').isalnum()
        assert is_alphanumeric, f"Tool name '{v}' must be alphanumeric."
        return v

    async def run_async(self, tool_input: str) -> str:
        pass
