from abc import ABC, abstractmethod
from typing import Optional, AsyncGenerator, List, Union, Callable, Awaitable, Literal

from skyframe.utils import logger
from ..models import TextGenerationRequest, TextResponse, \
    TextGenerationParams, TextResponseChunk

StreamCallback = Callable[[TextResponseChunk], None]
StreamCallbacks = Union[StreamCallback, List[StreamCallback]]

AsyncStreamCallback = Callable[[TextResponseChunk], Awaitable[None]]
AsyncStreamCallbacks = Union[AsyncStreamCallback, List[AsyncStreamCallback]]

# Token usage pricing for different models. Prices in USD per 1M tokens.
PRICING_DICT = {
    # OpenAI models
    'gpt-4o': {
        'input': 5.0,
        'output': 15.0,
    },
    'gpt-3.5-turbo-0125': {
        'input': 0.5,
        'output': 1.5,
    },
    'gpt-3.5-turbo-instruct': {
        'input': 1.5,
        'output': 2.0,
    },
    'gpt-4-turbo': {
        'input': 10.0,
        'output': 30.0,
    },
    'gpt-4': {
        'input': 30.0,
        'output': 60.0,
    },
    'gpt-4-32k': {
        'input': 60.0,
        'output': 120.0,
    },

    # Anthropic models
    'claude-3-5-sonnet-20240620': {
        'input': 3.0,
        'output': 15.0,
    },
    'claude-3-opus-20240229': {
        'input': 15.0,
        'output': 75.0,
    },
    'claude-3-sonnet-20240229': {
        'input': 3.0,
        'output': 15.0,
    },
    'claude-3-haiku-20240307': {
        'input': 0.25,
        'output': 1.25,
    },
    'claude-2.1': {
        'input': 8.0,
        'output': 24.0,
    },
    'claude-2.0': {
        'input': 8.0,
        'output': 24.0,
    },
    'claude-instant-1.2': {
        'input': 0.8,
        'output': 2.4,
    }
}


class BaseTextGenerationService(ABC):
    @staticmethod
    @abstractmethod
    def get_token_count(
            request: TextGenerationRequest,
            generation_info: Optional[Union[str, TextGenerationParams]]
    ) -> int:
        pass

    @staticmethod
    def _get_cost_per_token(
            model_name: str,
            cost_type: Literal['input', 'output']
    ):
        cost_per_token = None
        try:
            model = PRICING_DICT[model_name]
            cost_per_token = model[cost_type] / 1_000_000
        except KeyError:
            for key in PRICING_DICT.keys():
                if key in model_name:
                    cost_per_token = PRICING_DICT[key][cost_type] / 1_000_000
                    break

        if not cost_per_token:
            cost_per_token = 5 / 1_000_000
            logger.warning(
                f"Could not find cost for model '{model_name}'. Using default cost of {cost_per_token} per token."
            )

        return cost_per_token

    @staticmethod
    def get_cost_per_input_token(
            model_name: str,
    ) -> float:
        return BaseTextGenerationService._get_cost_per_token(model_name, 'input')

    @staticmethod
    def get_cost_per_output_token(
            model_name: str,
    ) -> float:
        return BaseTextGenerationService._get_cost_per_token(model_name, 'output')

    @staticmethod
    def calculate_cost(
            token_count: int,
            model_name: str,
    ) -> float:
        cost_per_token = BaseTextGenerationService.get_cost_per_output_token(model_name)
        return round(token_count * cost_per_token, 6)

    @abstractmethod
    def run(
            self,
            request: TextGenerationRequest,
            generation_params: TextGenerationParams,
    ) -> TextResponse:
        pass

    @abstractmethod
    async def run_async(
            self,
            request: TextGenerationRequest,
            generation_params: TextGenerationParams,
    ) -> TextResponse:
        pass

    @abstractmethod
    async def run_stream(
            self,
            request: TextGenerationRequest,
            generation_params: TextGenerationParams,
    ) -> AsyncGenerator[TextResponseChunk, None]:
        pass
