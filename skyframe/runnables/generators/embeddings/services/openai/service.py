import os

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI
from openai.types import CreateEmbeddingResponse

from skyframe.utils import logger
from ..base import BaseEmbeddingsGenerationService
from .converter import OpenAiEmbeddingsGenerationConverter
from ...models import EmbeddingsGenerationRequest, EmbeddingsGenerationParams, EmbeddingsResponse


class OpenAiEmbeddingsGenerationService(BaseEmbeddingsGenerationService):
    client: AsyncOpenAI
    client_sync: OpenAI
    converter: OpenAiEmbeddingsGenerationConverter
    default_model: str = 'text-embedding-3-small'

    def __init__(self):
        super().__init__()
        load_dotenv()
        api_key = os.environ.get('OPENAI_API_KEY')
        self.client = AsyncOpenAI(api_key=api_key)
        self.client_sync = OpenAI(api_key=api_key)
        self.converter = OpenAiEmbeddingsGenerationConverter()

    @staticmethod
    def calculate_cost(
            token_count: int,
            model_name: str,
    ) -> float:
        pricing = {
            'text-embedding-3-small': 0.00002,
            'text-embedding-3-large': 0.00013,
            'text-embedding-ada-002': 0.0001,
        }

        cost_per_token = None

        try:
            cost_per_token = pricing.get(model_name, 0.00002) / 1000
        except KeyError:
            for key in pricing.keys():
                if key in model_name:
                    cost_per_token = pricing[key] / 1000
                    break

        if not cost_per_token:
            cost_per_token = 0.001 / 1000
            logger.warning(
                f"Could not find cost for model '{model_name}'. Using default cost of {cost_per_token}."
            )

        return round(token_count * cost_per_token, 6)

    def run(
            self,
            request: EmbeddingsGenerationRequest,
            generation_params: EmbeddingsGenerationParams
    ) -> EmbeddingsResponse:
        if request is None:
            raise ValueError("EmbeddingsGenerationRequest cannot be None")

        logger.dev_debug(request)
        logger.dev_debug(generation_params)

        openai_params = self.converter.to_embedding_create_params(
            request=request,
            generation_params=generation_params
        )

        logger.dev_debug(openai_params)

        embeddings_response: CreateEmbeddingResponse = self.client_sync.embeddings.create(
            **openai_params
        )

        logger.dev_debug(embeddings_response)

        response = self.converter.from_create_embedding_response(embeddings_response)

        logger.dev_debug(response)

        return response

    async def run_async(
            self,
            request: EmbeddingsGenerationRequest,
            generation_params: EmbeddingsGenerationParams
    ) -> EmbeddingsResponse:
        if request is None:
            raise ValueError("EmbeddingsGenerationRequest cannot be None")

        logger.dev_debug(request)
        logger.dev_debug(generation_params)

        openai_params = self.converter.to_embedding_create_params(
            request=request,
            generation_params=generation_params
        )

        logger.dev_debug(openai_params)

        embeddings_response: CreateEmbeddingResponse = await self.client.embeddings.create(
            **openai_params
        )

        logger.dev_debug(embeddings_response)

        response = self.converter.from_create_embedding_response(embeddings_response)

        logger.dev_debug(response)

        return response