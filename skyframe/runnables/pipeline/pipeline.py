from typing import Any, List

from pydantic import Field

from .models.params import PipelineParams
from ..base import Runnable


class Pipeline(Runnable):
    pipeline_params: PipelineParams = Field(default_factory=PipelineParams)

    runnables: List[Runnable] = Field(default_factory=list)

    def add_runnable(self, runnable: Runnable):
        self.runnables.append(runnable)

    async def run_async(self, **data) -> Any:
        cur_data = data

        for runnable in self.runnables:
            cur_data = await runnable.run_async(**cur_data)
        return data
