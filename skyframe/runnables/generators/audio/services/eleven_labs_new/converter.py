from typing import Dict, Any
from elevenlabs.types import VoiceSettings

from skyframe.exceptions import ConversionException
from ...models import AudioGenerationRequest, AudioGenerationParams


class ElevenLabsGenerationConverter:
    """
    A class for converting between Quiply and Elevenlab objects.

    :raises ConversionException: If the conversion fails.
    """

    @staticmethod
    def to_request(
            request: AudioGenerationRequest,
            generation_params: AudioGenerationParams,
    ) -> Dict[str, Any]:
        """
        Convert a Quiply AudioGenerationRequest to an Elevenlabs request.

        :param request: The Quiply AudioGenerationRequest to convert.
        :param generation_params: The Quiply AudioGenerationParams to convert.

        :return: The converted Elevenlabs request.
        """

        try:
            request_dict: Dict[str, Any] = {}

            voice_settings = ElevenLabsGenerationConverter.to_voice_settings(generation_params)
            request_dict['text'] = request
            request_dict['voice'] = generation_params.voice_id
            request_dict['voice_settings'] = voice_settings
            request_dict['model'] = generation_params.model
            request_dict['stream'] = False
            request_dict['output_format'] = generation_params.output_format

            return request_dict

        except ConversionException as e:
            raise e
        except Exception as e:
            raise ConversionException(
                ElevenLabsGenerationConverter,
                from_type=AudioGenerationRequest,
                to_type=Dict[str, Any],
                inner_exception=e,
            )

    @staticmethod
    def to_voice_settings(generation_params: AudioGenerationParams) -> VoiceSettings:
        try:
            voice_settings = VoiceSettings(
                stability=generation_params.stability,
                similarity_boost=generation_params.similarity_boost,
                style=generation_params.style,
                use_speaker_boost=generation_params.use_speaker_boost,
            )
            return voice_settings
        except Exception as e:
            raise ConversionException(
                ElevenLabsGenerationConverter,
                from_type=AudioGenerationParams,
                to_type=VoiceSettings,
                inner_exception=e,
            )