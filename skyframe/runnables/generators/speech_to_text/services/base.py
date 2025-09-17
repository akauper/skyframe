from abc import ABC, abstractmethod

from ..models import SpeechToTextGenerationParams, SpeechToTextResponse, SpeechToTextRequest


class BaseSpeechToTextGenerationService(ABC):

    @abstractmethod
    async def run_async(
            self,
            request: SpeechToTextRequest,
            generation_params: SpeechToTextGenerationParams,
    ) -> SpeechToTextResponse:
        pass
