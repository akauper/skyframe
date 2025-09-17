from abc import ABC, abstractmethod

from ..models import ModerationResponse, ModerationGenerationParams


class BaseModerationService(ABC):

    @abstractmethod
    def run(
            self,
            request: str,
            generation_params: ModerationGenerationParams
    ) -> ModerationResponse:
        pass

    @abstractmethod
    async def run_async(
            self,
            request: str,
            generation_params: ModerationGenerationParams
    ) -> ModerationResponse:
        pass
