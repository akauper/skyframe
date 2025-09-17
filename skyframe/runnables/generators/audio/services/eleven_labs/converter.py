from typing import Any, Dict

from elevenlabs import VoiceSettings

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

        request_dict: Dict[str, Any] = {}

        try:
            if isinstance(request, str):
                request_dict['text'] = request
            else:
                request_dict['input_text_iterator'] = request

            voice_id = generation_params.voice_id
            voice_settings = ElevenLabsGenerationConverter.to_voice_settings(generation_params)
            request_dict['voice_settings'] = voice_settings
            # voice = Voice(
            #     voice_id=generation_params.voice_id,
            #     settings=voice_settings,
            # )

            request_dict['voice_id'] = voice_id
            request_dict['model'] = generation_params.model
            request_dict['stream'] = False
            request_dict['latency'] = generation_params.latency
            request_dict['output_format'] = generation_params.output_format
            request_dict['stream_chunk_size'] = generation_params.stream_chunk_size
            request_dict['text_chunker'] = generation_params.text_chunker

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

    # @staticmethod
    # def to_voice(generation_params: AudioGenerationParams) -> Voice:
    #     try:
    #         voice_settings = ElevenLabsGenerationConverter.to_voice_settings(generation_params)
    #         voice = Voice(
    #             voice_id=generation_params.voice_id,
    #             settings=voice_settings,
    #         )
    #         return voice
    #     except ConversionException as e:
    #         raise e
    #     except Exception as e:
    #         raise ConversionException(
    #             ElevenLabsGenerationConverter,
    #             from_type=AudioGenerationParams,
    #             to_type=Voice,
    #             inner_exception=e,
    #         )

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

    @staticmethod
    def to_voice_settings_dict(voice_settings: VoiceSettings) -> Dict[str, Any]:
        try:
            return {
                'stability': voice_settings.stability,
                'similarity_boost': voice_settings.similarity_boost,
                'style': voice_settings.style,
                'use_speaker_boost': voice_settings.use_speaker_boost
            }
        except Exception as e:
            raise ConversionException(
                ElevenLabsGenerationConverter,
                from_type=VoiceSettings,
                to_type=Dict[str, Any],
                inner_exception=e,
            )
