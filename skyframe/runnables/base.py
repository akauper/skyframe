from abc import ABC, abstractmethod
from typing import Any, List, Optional, TypeVar
from uuid import uuid4, UUID

from pydantic import BaseModel, Field
from typing_extensions import Unpack

from skyframe.utils import logger
from .models.params import RunnableParams
from .models.run_info import RunInfo, RunContext


class Runnable(BaseModel, ABC):
    process_id: Optional[str] = Field(default=None)
    runnable_params: RunnableParams = Field(default_factory=RunnableParams)


    def try_set(self, **data: Any) -> List[str]:
        return self.runnable_params.try_set(**data)

    def cleanup(self):
        del self.runnable_params

    def __pretty__(self, fmt: Any, **kwargs: Any) -> Any:
        yield ' '
        yield 1
        yield 'Runnable'
        yield 1
        yield f'Runnable Params: {self.runnable_params}'
        yield -1
        yield 0

    @abstractmethod
    async def run_async(self, **kwargs: Any) -> Any:
        pass

    def run(self, **kwargs: Any) -> Any:
        pass

    def _begin_run(
            self,
            *,
            run_id: UUID = None,
            parent_run_id: UUID = None,
            **kwargs
    ) -> RunContext:
        run_info = RunInfo(
            process_id=self.process_id,
            run_id=run_id or uuid4(),
            parent_run_id=parent_run_id or None,
            runnable_params=self.runnable_params,
        )
        run_ctx: RunContext = {
            'info': run_info,
            **kwargs
        }
        return run_ctx

    async def _invoke_callback_async(self, name: str, **kwargs: Unpack[RunContext]) -> None:
        try:
            if self.runnable_params.callbacks:
                for callback in self.runnable_params.callbacks:
                    func = getattr(callback, name, None)
                    if not func or not callable(func) or not hasattr(callback, name):
                        logger.error(f"Callback {callback} does not have method {name}")
                        continue

                    await func(**kwargs)
                    if 'start' in name:
                        await callback.on_any_start(callback_name=name, **kwargs)
                    elif 'error' in name:
                        await callback.on_any_error(callback_name=name, **kwargs)
                    elif 'end' in name:
                        await callback.on_any_end(callback_name=name, **kwargs)
        except Exception as e:
            logger.exception(f"Error invoking callback {name}: {e}")


TRunnable = TypeVar("TRunnable", bound=Runnable)
