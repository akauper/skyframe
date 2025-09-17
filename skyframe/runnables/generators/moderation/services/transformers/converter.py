from skyframe.exceptions import ConversionException
from ...models import ModerationParameter, ModerationResponse


class TransformersModerationConverter:
    """
    A class for converting between Quiply and Transformers moderation objects.

    :raises ConversionException: If the conversion fails.
    """

    @staticmethod
    def from_transformer_response(model: str, response: list) -> ModerationResponse:
        """
        Convert a Transformers response to a Quiply ModerationResult.

        :param model: The model used to generate the moderation results.
        :param response: The Transformers response to convert.
        :return: The converted Quiply ModerationResult.
        """
        try:
            has_injection = 'injection' in response[0]['label'].lower()
            return ModerationResponse(
                model=model,
                flagged=has_injection,
                prompt_injection=ModerationParameter(
                    flagged=has_injection,
                    score=response[0]['score']
                )
            )
        except Exception as e:
            raise ConversionException(
                TransformersModerationConverter,
                from_type=ModerationParameter,
                to_type=ModerationResponse,
                inner_exception=e
            )
