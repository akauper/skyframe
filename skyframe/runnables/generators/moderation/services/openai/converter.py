from typing import Any, Dict

from openai.types import ModerationCreateResponse

from skyframe.exceptions import ConversionException
from ...models import ModerationResponse, ModerationParameter


class OpenaiModerationConverter:
    """
    A class for converting between Quiply and OpenAI moderation objects.

    :raises ConversionException: If the conversion fails.
    """

    @staticmethod
    def from_moderation_create_response(response: ModerationCreateResponse) -> ModerationResponse:
        """
        Convert a OpenAI ModerationCreateResponse to a Quiply ModerationResult.

        :param response: The OpenAI ModerationCreateResponse to convert.
        :return: The converted Quiply ModerationResult.
        """
        try:
            result_dict: Dict[str, Any] = {
                "model": response.model,
                "flagged": response.results[0].flagged
            }

            moderation = response.results[0]
            for category in moderation.categories:
                key = category[0]
                flagged = category[1]
                score = moderation.category_scores.model_dump().get(key, 0.0)

                result_dict.setdefault(key, ModerationParameter(flagged=flagged, score=score))

            return ModerationResponse.model_validate(result_dict)
        except Exception as e:
            raise ConversionException(
                OpenaiModerationConverter,
                from_type=ModerationCreateResponse,
                to_type=ModerationResponse,
                inner_exception=e
            )
