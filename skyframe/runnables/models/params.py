from typing import List

from pydantic import Field

from skyframe.models.base import BaseParams
from .callback import BaseAsyncCallback
from .metadata import RunnableMetadata


class RunnableParams(BaseParams):
    callbacks: List[BaseAsyncCallback] = Field(default_factory=list)
    metadata: RunnableMetadata = Field(default_factory=RunnableMetadata)

    verbose: bool = Field(default=False)
    """ Whether to print debug information. """

    # def try_set(self, **kwargs: Any) -> Optional[Dict[str, Any]]:
    #     unused = super().try_set(**kwargs)
    #
    #     for k, v in kwargs.items():
    #         if k == 'callbacks' and v is not None and isinstance(v, list):
    #             self.callbacks.extend(v)
    #         else:
    #             unused[k] = v
    #     return unused
