from abc import ABC
from datetime import datetime
from typing import Any, List, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field


class UIDMixin(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    """ A unique identifier for the object. """


class CreatedAtMixin(BaseModel):
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    """ The timestamp (in iso format) of when the object was created. """


class UpdatedAtMixin(BaseModel):
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    """ The timestamp (in iso format) of when the object was updated. """

    def update_timestamp(self):
        self.updated_at = datetime.now().isoformat()


class BaseParams(BaseModel, ABC):

    _TParams = TypeVar('_TParams', bound='BaseParams')

    def try_set(self, **kwargs: Any) -> List[str]:  # Returns a list of used keys
        used: List[str] = []

        my_dict = self.model_dump()
        for k, v in kwargs.items():
            if k in my_dict:
                self.__setattr__(k, v)
                used.append(k)
        return used

    def merge(self, other: _TParams) -> _TParams:
        """
        Merges another BaseParams into this one.
        All values in the 'other' BaseParams will overwrite the values in this one.

        :param other: The other BaseParams.
        :return: A new BaseParams object.
        """

        new_model = self.model_copy()

        if other is None:
            return new_model

        for k, v in other.model_dump(exclude_unset=True, exclude_defaults=True, exclude_none=True).items():
            if k == 'stop':
                new_model.add_stop(v)
            else:
                setattr(new_model, k, v)

        return new_model
