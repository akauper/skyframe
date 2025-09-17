from abc import ABC, abstractmethod
from typing import ClassVar, Type, Dict, Any, TypeVar, List, Generic
from uuid import uuid4

from devtools import debug
from pydantic import BaseModel, Field
from ..results.base_result import TResult

TInput = TypeVar('TInput')
TResolvable = TypeVar('TResolvable', bound='BaseResolvable')


class BaseResolvable(BaseModel, ABC, Generic[TInput, TResult]):
    type: ClassVar[str]

    id: str = Field(default_factory=lambda: str(uuid4()))

    @abstractmethod
    async def resolve_async(self, input: TInput) -> TResult:
        pass

    @classmethod
    def _get_subclasses_list_recursive(cls):
        """
        Gets all subclasses of BaseResolvable class recursively.
        It's important to note that these subclasses must be imported in the file where this method is called.
        """

        subclasses = []
        for subclass in cls.__subclasses__():
            if getattr(subclass, 'type', None) is not None:
                subclasses.append(subclass)
            subclasses.extend(subclass._get_subclasses_list_recursive())
        return subclasses

    @classmethod
    def get_subclass_of_type(cls, type: str) -> Type[TResolvable]:
        """
        Gets a subclass of BaseResolvable with a specific 'type' class variable.
        It's important to note that any subclasses must be imported in the file where this method is called.
        """
        subclasses = cls._get_subclasses_list_recursive()
        for subclass in subclasses:
            if subclass.type == type:
                return subclass

        debug(subclasses)
        raise ValueError(f'No subclass with type {type} found for {cls.__name__}')

    @classmethod
    def model_validate_subclass(cls, data: Dict[str, Any]) -> TResolvable:
        if 'type' in data:
            instance_type = data['type']
            del data['type']
            instance_cls = cls.get_subclass_of_type(instance_type)
            return instance_cls.model_validate(data)
        raise ValueError(f'No type found in {data}')

    @classmethod
    def model_validate_subclasses(cls, data_dicts: List[Dict[str, Any]]) -> List[TResolvable]:
        return [cls.model_validate_subclass(data_dict) for data_dict in data_dicts]
