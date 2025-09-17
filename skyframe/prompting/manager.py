import glob
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

from skyframe.utils import logger
from .models import PromptStructure, EvaluablePrompt
from .utils import _get_nested_value, _set_nested_value, _format_list_items, _combine_dict_to_str
from ..settings import framework_settings
from ..utils import get_framework_path

_alternatives_folder_name = 'alternatives'
_prompts_folder_name = 'prompts'


class PromptManager:
    prompt_dict: Dict
    _flattened_prompt_dict: Dict

    _loaded_files: List[str] = []

    def __init__(self):
        self.formatted_prompts_data = self._load_formatted_prompts_data()
        formatted_alternatives_data = self._load_formatted_alternatives_data()

        self.prompt_dict = self._build_prompt_dict(self.formatted_prompts_data, formatted_alternatives_data)
        self._flattened_prompt_dict = self._flatten_prompt_dict(self.prompt_dict)

        logger.info(
            f"Loaded {len(self._flattened_prompt_dict.keys())} prompts from {len(self._loaded_files)} files.")
        if logger.is_debug():
            alternatives_count = 0
            for prompt in self._flattened_prompt_dict.values():
                alternatives_count += len(prompt.alternatives)
            logger.debug(f"And {alternatives_count} alternatives.")

    def get_prompt_by_name(self, name: str) -> EvaluablePrompt | None:
        """Returns the PromptValue with the given name, or None if it doesn't exist."""
        return self._flattened_prompt_dict.get(name, None)

    def _load_formatted_prompts_data(self) -> Dict:
        # Load the default prompts from yaml files into a dictionary that is [filename][data_dict]
        prompts_file_dict = self._load_yaml_data(_prompts_folder_name)
        # Merge all files into one dict. Final structure is just the raw data dict.
        # We should have entries like 'character.instructions': 'some text'
        merged_prompts_data = self._merge_yaml_data(list(prompts_file_dict.keys()), list(prompts_file_dict.values()))
        # Format the data
        return self._format_data(merged_prompts_data)

    def _load_formatted_alternatives_data(self) -> Dict:
        # Load the default alternatives from yaml files into a dictionary that is [filename][data_dict]
        # Note that we will have filenames like debate_v1.yaml and debate_v2.yaml
        # We cant just merge them like we did with prompts. We need to deal with alternative keys (v1, v2, etc...)
        alternatives_file_dict = self._load_yaml_data(_alternatives_folder_name)
        # Structure for alternatives should be [alternative_key][data_dict]
        # We should have entries like 'v1' -> 'character.instructions': 'some text'
        merged_alternatives_data = {}
        for k, v in alternatives_file_dict.items():
            if v is not None:
                base_name, _, suffix = k.rpartition('_')
                suffix = suffix.lower()[:-len('.yaml')]
                merged_alternatives_data.setdefault(suffix, {})
                merged_alternatives_data[suffix].update(v)
        # Format the data
        return self._format_data(merged_alternatives_data)

    def _load_yaml_data(self, folder_name: str) -> Dict[str, Dict]:
        """Returns a dict of all the YAML files in the given folder. Keys are the file names, values are the file contents."""
        # script_dir = Path(__file__).parent
        rel_data_dir = framework_settings.prompting.data_dir
        prompting_dir = get_framework_path() / rel_data_dir
        path = prompting_dir / folder_name
        pattern = str(path / '**' / '*.yaml')
        files = glob.glob(pattern, recursive=True)
        file_dict = {}
        for file in files:
            file_name = Path(file).name
            file_dict[file_name] = self._load_yaml_file(file)
            self._loaded_files.append(file)  # For logging and Debugging

        return file_dict

    def load_all_yaml_files(self) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
        """Returns a tuple of all the YAML data in the prompts and alternatives directories."""
        prompts_file_dict = self._load_yaml_data(_prompts_folder_name)
        alternatives_file_dict = self._load_yaml_data(_alternatives_folder_name)
        return prompts_file_dict, alternatives_file_dict

    @staticmethod
    def _merge_yaml_data(keys: List[str], data_dicts: List[Dict]) -> Dict:
        """Merges a list of dicts into one dict."""
        merged_dict = {}

        for i in range(len(keys)):
            key = keys[i]
            data = data_dicts[i]
            if data is not None:
                data['file_name'] = key
                merged_dict.update(data)

        # for data in data_dicts:
        #     merged_dict.update(data)
        return merged_dict

    @staticmethod
    def _load_yaml_file(file_path: str):
        """Loads a YAML file."""
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)

    def _format_data(self, raw_data: Dict) -> Dict:
        data = {}
        for k, v in raw_data.items():
            if isinstance(v, list):
                data[k] = _format_list_items(v)  # Format our lists
            elif isinstance(v, dict):
                if (combine := v.get('combine', None)) is not None:
                    key_format = combine.get('key_format', "**{key}**: ")
                    del v['combine']
                    data[k] = _combine_dict_to_str(v, key_format)  # Format our dicts with 'combine' in them
                else:
                    data[k] = self._format_data(v)
            else:
                data[k] = v  # This is where we would format strings if we need to.
        return data

    @staticmethod
    def _build_prompt_dict(prompts_data: Dict, alternatives_data: Dict):
        result = {}

        def get_alternatives(data_key: str, data_path: List[str]) -> Dict[str, str]:
            """Returns a dict of all the alternatives at the specified path."""
            alternatives: Dict[str, str] = {}
            # Since our alternatives_data is structured like [alternative_key][data_dict]
            # We need to get the data dict for the current alternative key
            for key, value in alternatives_data.items():
                # Try to get the nested value inside the alternatives data dict. This should be a string
                alt_data = _get_nested_value(value, data_path, None)
                if alt_data is None or not isinstance(alt_data, str):
                    continue
                alternatives[key] = alt_data

            return alternatives

        def process_dict(current_path: List[str], data: Dict):
            for k, v in data.items():
                path = current_path + [k]
                if isinstance(v, Dict):
                    if _get_nested_value(result, path, None) is None:
                        _set_nested_value(result, path, {})
                    process_dict(path, v)
                elif isinstance(v, str):
                    name = '.'.join(path)

                    alternatives = get_alternatives(k, path)
                    prompt_template = EvaluablePrompt(name=name, template=v, scenario=path[0],
                                                      alternatives=alternatives)
                    _set_nested_value(result, path, prompt_template)

        process_dict([], prompts_data)
        return result

    @staticmethod
    def _flatten_prompt_dict(prompts_data: Dict):
        result = {}

        def process_dict(data: Dict):
            for k, v in data.items():
                if isinstance(v, EvaluablePrompt):
                    result[v.name] = v
                else:
                    process_dict(v)

        process_dict(prompts_data)
        return result


try:
    prompt_manager = PromptManager()
    prompts = PromptStructure.model_validate(prompt_manager.prompt_dict, from_attributes=True)
    f = 'a'
except Exception as e:
    logger.error(f"Error loading prompt manager: {e}")
    raise e
# loggers.evaluation.info(pprint.pformat(prompt_manager._prompt_dict, indent=4))


# class _FileVar(BaseModel):
#     name: str
#     scenario: str
#     key: str
#     value: str


# class PromptAlternativeManager:
#     """Manages all the PromptAlternatives in the alternatives directory."""
#     _prompt_alternatives_by_name: Dict[str, QuiplyPromptValue]  # Key is the name of the alternative
#
#     def __init__(self):
#         self._prompt_alternatives_by_name = {}
#         self._load_alternatives()
#
#     @property
#     def prompt_alternatives(self) -> List[QuiplyPromptValue]:
#         """Returns a list of all the PromptAlternatives."""
#         return list(self._prompt_alternatives_by_name.values())
#
#     def get_alternative_by_name(self, name: str) -> QuiplyPromptValue | None:
#         """Returns the PromptAlternative with the given name, or None if it doesn't exist."""
#         return self._prompt_alternatives_by_name.get(name, None)
#
#     def get_alternatives_with_key(self, key: str) -> List[QuiplyPromptValue]:
#         """Returns a list of all the PromptAlternatives that have the given key."""
#         return [alternative for alternative in self._prompt_alternatives_by_name.values() if key in alternative.alternatives]
#
#     def get_templates_with_key(self, key: str) -> List[str]:
#         """Returns a list of all the PromptTemplates that have the given key."""
#         return [alternative.alternatives[key] for alternative in self.get_alternatives_with_key(key)]
#
#     def _load_alternatives(self):
#         """Loads all the PromptAlternatives from the files in the alternatives directory."""
#         files = self._get_py_files()
#         for file in files:
#             try:
#                 file_vars = self._get_file_vars(file)
#             except (IOError, ValidationError, SyntaxError) as e:
#                 logger.exception(f"Error processing file {file}: {e}")
#                 continue
#
#             for file_var in file_vars:
#                 alternative = self._prompt_alternatives_by_name.setdefault(file_var.name, QuiplyPromptValue(name=file_var.name, scenario=file_var.scenario))
#                 alternative.alternatives[file_var.key] = file_var.value
#         loggers.evaluation.info(f"Loaded {len(self._prompt_alternatives_by_name)} prompt alternatives from {len(files)} files.")
#         loggers.evaluation.debug(f"Prompt alternatives: {format_dict(self._prompt_alternatives_by_name, indent=4)}")
#
#     @staticmethod
#     def _get_file_vars(file_path: str) -> List[_FileVar]:
#         """Returns a dict of all the string variables in the file. Keys are the variable names, values are the variable values."""
#         string_vars = {}
#         scenario = Path(file_path).parent.name
#         with open(file_path, 'r') as f:
#             file_content = f.read()
#             try:
#                 exec(file_content, {}, string_vars)
#             except SyntaxError as e:
#                 raise ValidationError(f"Syntax error in file {file_path}: {e}")
#
#         file_vars: List[_FileVar] = []
#         for var_name, var_value in string_vars.items():
#             if isinstance(var_value, str):
#                 file_vars.append(PromptAlternativeManager._string_var_to_file_var(var_name, var_value, scenario))
#
#         return file_vars
#
#     @staticmethod
#     def _string_var_to_file_var(full_name: str, value: str, scenario_name: str) -> _FileVar:
#         """Converts a variable name to a _VarValue object using rpartition."""
#         base_name, _, suffix = full_name.rpartition('_')
#         return _FileVar(
#             name=base_name,
#             scenario=scenario_name,
#             key=suffix.lower(),
#             value=value,
#         )
#
#     @staticmethod
#     def _get_py_files() -> List[str]:
#         """Returns a list of all the python files in the alternatives directory."""
#         script_dir = Path(__file__).parent
#         alternatives_path = script_dir / 'alternatives'
#         pattern = str(alternatives_path / '**' / '*.py')
#         py_files = glob.glob(pattern, recursive=True)
#         return py_files
#
#     def create_c_prompt(self, template_name: str, template_value: str):
#         alternative = self.get_alternative_by_name(template_name)
#         return PromptTemplate.from_template(template_value).configurable_alternatives(
#             ConfigurableField(id="prompt"),
#             **alternative.alternatives
#         )
#

# from .load_yaml import prompts
# loggers.evaluation.info(json.dumps(prompts, indent=4))
# alternative_manager = PromptAlternativeManager()
