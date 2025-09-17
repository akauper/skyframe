from openai.types import CreateEmbeddingResponse, EmbeddingCreateParams

from skyframe.exceptions.conversion import ConversionException
from skyframe.models import TokenUsage
from ...models.response import EmbeddingsResponse
from ...models.request import EmbeddingsGenerationRequest
from ...models.generation_params import EmbeddingsGenerationParams


class OpenAiEmbeddingsGenerationConverter:

    @staticmethod
    def to_embedding_create_params(
            request: EmbeddingsGenerationRequest,
            generation_params: EmbeddingsGenerationParams,
    ):
        """
        Converts a Quiply EmbeddingsGenerationParams object to an OpenAi CreateEmbeddingParams TypedDict.

        :param request: The Quiply EmbeddingsGenerationRequest.
        :param generation_params: The Quiply EmbeddingsGenerationParams.
        :return: The converted OpenAi CreateEmbeddingParams.
        """
        try:
            params_dict = generation_params.model_dump(exclude_none=True)
            return EmbeddingCreateParams(
                input=request,
                **params_dict
            )
        except Exception as e:
            raise ConversionException(
                OpenAiEmbeddingsGenerationConverter,
                from_type=EmbeddingsGenerationParams,
                to_type=EmbeddingCreateParams,
                inner_exception=e
            )

    @staticmethod
    def from_create_embedding_response(response: CreateEmbeddingResponse) -> EmbeddingsResponse:
        """
        Converts an OpenAI CreateEmbeddingResponse to a Quiply EmbeddingsResponse.

        :param response: The OpenAI CreateEmbeddingResponse to convert.
        :return: The converted Quiply EmbeddingsResponse.
        """

        try:
            from .service import OpenAiEmbeddingsGenerationService
            total_tokens = response.usage.total_tokens
            prompt_tokens = response.usage.prompt_tokens
            total_cost = OpenAiEmbeddingsGenerationService.calculate_cost(total_tokens, response.model)
            prompt_cost = OpenAiEmbeddingsGenerationService.calculate_cost(prompt_tokens, response.model)

            return EmbeddingsResponse(
                data=response.data,
                model=response.model,
                token_usage=TokenUsage(
                    total=total_tokens,
                    prompt=prompt_tokens,
                    total_cost=total_cost,
                    prompt_cost=prompt_cost
                )
            )
        except Exception as e:
            raise ConversionException(
                OpenAiEmbeddingsGenerationConverter,
                from_type=CreateEmbeddingResponse,
                to_type=EmbeddingsResponse,
                inner_exception=e
            )
