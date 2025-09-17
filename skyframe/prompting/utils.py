from typing import Dict, List, Any

from skyframe.utils import add_tab_to_each_line

_list_item_prefix = '- '


# def get_evaluation_prompt(prompt: RunnableSerializable[dict, PromptValue] | PromptTemplate) -> PromptTemplate:
#     from src.config import quiply_settings
#
#     if isinstance(prompt, PromptTemplate):
#         return prompt
#     if not quiply_settings.evaluation.enabled:
#         return prompt.default
#
#     key = quiply_settings.evaluation.evaluation_prompt_key
#     if key not in prompt.alternatives:
#         return prompt.default
#
#     return prompt.alternatives[key]


def _get_nested_value(data_dict: Dict, keys: List[str], default=None) -> Any:
    for key in keys:
        if isinstance(data_dict, dict) and key in data_dict:
            data_dict = data_dict[key]
        else:
            return default
    return data_dict


def _set_nested_value(data_dict: Dict, key_path: List[str], value: Any):
    for key in key_path[:-1]:
        if key not in data_dict or not isinstance(data_dict[key], dict):
            data_dict[key] = {}
        data_dict = data_dict[key]
    data_dict[key_path[-1]] = value


def _combine_dict_to_str(data: Dict, key_format: str) -> str:
    result = ''
    for k, v in data.items():
        key_name = _format_key_name(k, key_format)

        if isinstance(v, list):
            result += f"{key_name}\n{_format_list_items(v)}\n"
        else:
            result += f"{key_name}{v}\n"
    return result


def _format_key_name(key: str, key_format: str) -> str:
    """Formats a key name to be more human-readable in combined dicts."""
    words = key.split('_')
    key_name = ' '.join(word.capitalize() for word in words)
    key_name = key_format.format(key=key_name)
    return key_name


def _format_list_items(items: List[str]) -> str:
    """This assumes all lists only have strings in them..."""
    return add_tab_to_each_line('\n'.join(_list_item_prefix + item for item in items))
