from abc import ABC
from typing import TypeVar, Generic, Any, ClassVar, Self

from devtools import debug
from pydantic import Field, model_validator

from ..base import Runnable
from ..models.params import BaseParams
from ...settings import framework_settings

TParams = TypeVar("TParams", bound=BaseParams)


class BaseGenerator(Runnable, ABC, Generic[TParams]):
    service_name: str = Field(default="UNSET")
    generation_params: TParams

    # Class variable to be enforced in subclasses
    generator_name: ClassVar[str]

    def __new__(cls, *args, **kwargs):
        # Ensure that subclasses have defined generator_name
        if not hasattr(cls, 'generator_name') or cls.generator_name == "UNSET":
            raise TypeError("Subclasses of BaseGenerator must define a 'generator_name' class variable")
        return super().__new__(cls)

    @model_validator(mode='before')
    @classmethod
    def validate_load_settings(cls, data: Any) -> Self:
        # Use the class-level generator_name
        if not cls.generator_name or cls.generator_name == "UNSET":
            raise ValueError("Subclasses of BaseGenerator must define a 'generator_name' class variable")

        generator_settings = framework_settings.runnables.generators.model_dump().get(cls.generator_name)
        debug(generator_settings)

        tparams_cls = cls.__pydantic_core_schema__.get('schema').get('schema').get('fields').get(
            'generation_params').get('schema').get('cls')

        data['service_name'] = generator_settings.get('service_name', "UNSET") or "UNSET"
        data['generation_params'] = tparams_cls.model_validate(generator_settings.get('generation_params', {}))
        debug(data)
        return data
