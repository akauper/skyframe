import asyncio
import base64
import json
import os
from typing import Optional, Union, AsyncGenerator, AsyncIterator, Callable

import aiohttp
import requests
import websockets
from elevenlabs import Model, OutputFormat, VoiceSettings

from skyframe import framework_settings
from ...models import AudioResponse, AudioResponseChunk

from .converter import ElevenLabsGenerationConverter


async def default_text_chunker(chunks: AsyncIterator[str]) -> AsyncIterator[str]:
    """Used during input streaming to chunk text blocks and set last char to space"""
    splitters = (".", ",", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", " ")
    buffer = ""
    async for text in chunks:
        if buffer.endswith(splitters):
            yield buffer if buffer.endswith(" ") else buffer + " "
            buffer = text
        elif text.startswith(splitters):
            output = buffer + text[0]
            yield output if output.endswith(" ") else output + " "
            buffer = text[1:]
        else:
            buffer += text
    if buffer != "":
        yield buffer + " "


class ElevenLabsClient:
    url_base: str = framework_settings.runnables.generators.audio.get_service_value('eleven_labs', 'url_base') or "https://api.elevenlabs.io/v1"
    ws_url_base: str = framework_settings.runnables.generators.audio.get_service_value('eleven_labs', 'ws_url_base') or "wss://api.elevenlabs.io/v1"
    headers: dict = framework_settings.runnables.generators.audio.get_service_value('eleven_labs', 'headers') or {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
    }

    def __init__(self, api_key: Optional[str] = None):
        self.headers["xi-api-key"] = api_key or self._get_api_key()

    @staticmethod
    def _get_api_key() -> str:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("ELEVEN_LABS_API_KEY")
        if not api_key:
            raise ValueError("ELEVEN_LABS_API_KEY environment variable is not set")
        return api_key

    def generate(
            self,
            text: str,
            voice_id: str,
            voice_settings: VoiceSettings,
            model: Union[str, Model],
            output_format: OutputFormat,
    ) -> AudioResponse:
        """
        Generate audio synchronously.

        :return: AudioResponse
        """
        url, data = self._get_generation_data(False, text, voice_id, voice_settings, model, output_format, 1)

        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()

        response_str = base64.b64encode(response.content).decode("utf-8")
        return AudioResponse(audio=response_str)

    async def generate_async(
            self,
            text: str,
            voice_id: str,
            voice_settings: VoiceSettings,
            model: Union[str, Model],
            output_format: OutputFormat,
            **kwargs,
    ) -> AudioResponse:
        """
        Generate audio asynchronously.

        :return: AudioResponse
        """
        url, data = self._get_generation_data(False, text, voice_id, voice_settings, model, output_format, 1)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=data, headers=self.headers) as response:
                    if response.status == 200:
                        response_data = await response.read()
                        response_str = base64.b64encode(response_data).decode("utf-8")
                        return AudioResponse(audio=response_str)
                    else:
                        response_text = await response.text()
                        raise requests.exceptions.HTTPError(f"Failed to generate text-to-speech: {response_text}")
            except aiohttp.ClientError as e:
                raise e

    async def generate_async_stream_output(
            self,
            text: str,
            voice_id: str,
            voice_settings: VoiceSettings,
            model: Union[str, Model],
            output_format: OutputFormat,
            latency: int,
            stream_chunk_size: int,
            **kwargs
    ) -> AsyncGenerator[AudioResponseChunk, None]:
        """
        Generate audio asynchronously with streaming output.

        :return: AsyncGenerator[AudioResponseChunk, None]

        Example:
            async for chunk in client.generate_async_stream_output("Hello world"):
                if chunk.is_start:
                    print("Start of audio")
                elif chunk.is_final:
                    print("End of audio")
                else:
                    play(chunk.audio)
        """
        url, data = self._get_generation_data(True, text, voice_id, voice_settings, model, output_format, latency)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=data, headers=self.headers) as response:
                    if response.status == 200:
                        chunk_count = 0
                        yield AudioResponseChunk(index=chunk_count, is_start=True)
                        async for chunk in response.content.iter_chunked(stream_chunk_size):
                            if chunk:
                                chunk_count += 1
                                chunk_bytes = chunk
                                chunk_str = base64.b64encode(chunk_bytes).decode("utf-8")
                                yield AudioResponseChunk(index=chunk_count, audio=chunk_str)
                        yield AudioResponseChunk(index=chunk_count + 1, is_final=True)
                    else:
                        response_text = await response.text()
                        raise requests.exceptions.HTTPError(f"Failed to generate text-to-speech: {response_text}")
            except Exception as e:
                raise e

    async def generate_async_stream_full_duplex(
            self,
            input_text_iterator: AsyncIterator[str],
            voice_id: str,
            voice_settings: VoiceSettings,
            model: Union[str, Model],
            output_format: OutputFormat,
            latency: int,
            stream_chunk_size: int,
            text_chunker: Optional[Callable[[AsyncIterator[str]], AsyncIterator[str]]],
            **kwargs
    ) -> AsyncGenerator[AudioResponseChunk, None]:
        """
        Generate audio asynchronously with streaming input and output.

        :return: AsyncGenerator[Dict, None]

        Example:
            async for chunk in client.generate_async_stream_full_duplex(["Hello world"]):
                if chunk.is_start:
                    print("Start of audio")
                elif chunk.is_final:
                    print("End of audio")
                else:
                    play(chunk.audio)
        """
        bos = json.dumps(
            dict(
                text=" ",  # Eleven Labs requires a whitespace character to start streaming
                # try_trigger_generation=True,
                voice_settings=ElevenLabsGenerationConverter.to_voice_settings_dict(voice_settings) if voice_settings else None,
                # generation_config=dict(
                #     chunk_length_schedule=[50],
                # ),
                xi_api_key=self.headers["xi-api-key"]
            )
        )
        eos = json.dumps(dict(text=""))

        async def send():
            await websocket.send(bos)

            chunker = text_chunker or default_text_chunker
            prev_text = None
            cur_chunk = None
            async for text_chunk in chunker(input_text_iterator):
                if cur_chunk:
                    data = dict(
                        text=cur_chunk,
                        previous_text=prev_text,
                        next_text=text_chunk,
                        try_trigger_generation=True
                    )
                    await websocket.send(json.dumps(data))
                if prev_text:
                    prev_text += cur_chunk
                else:
                    prev_text = cur_chunk
                cur_chunk = text_chunk

            await websocket.send(json.dumps(dict(
                text=cur_chunk,
                previous_text=prev_text,
                next_text="",
                try_trigger_generation=True
            )))

            await websocket.send(eos)

        try:
            if isinstance(model, str):
                model = Model(model_id=model)

            uri = f"{self.ws_url_base}/text-to-speech/{voice_id}/stream-input?model_id={model.model_id}&output_format={output_format}&optimize_streaming_latency={latency}"

            async with websockets.connect(
                    uri,
                    # extra_headers={"xi-api-key": self.headers["xi-api-key"]}
            ) as websocket:
                send_task = asyncio.create_task(send())

                chunk_count = 0
                yield AudioResponseChunk(index=chunk_count, is_start=True)
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        if data.get('audio', None):
                            chunk_count += 1
                            chunk = AudioResponseChunk(
                                index=chunk_count,
                                audio=data['audio'],
                                normalized_alignment=data.get('normalizedAlignment', None),
                            )
                            yield chunk
                    except websockets.WebSocketException:
                        break
                yield AudioResponseChunk(index=chunk_count + 1, is_final=True)

                await send_task  # Wait for send task to finish (it should always be done)
        except websockets.WebSocketException as e:
            raise e

    def _get_generation_data(
            self,
            stream: bool,
            text: str,
            voice_id: str,
            voice_settings: VoiceSettings,
            model: Union[str, Model],
            output_format: OutputFormat,
            latency: int,
    ) -> (str, dict):
        if text is None:
            raise ValueError("Text cannot be None")

        if isinstance(model, str):
            model = Model(model_id=model)

        if stream:
            url = f"{self.url_base}/text-to-speech/{voice_id}/stream?optimize_streaming_latency={latency}&output_format={output_format}"
        else:
            url = f"{self.url_base}/text-to-speech/{voice_id}?output_format={output_format}"

        data = dict(
            model_id=model.model_id,
            text=text,
            voice_settings=ElevenLabsGenerationConverter.to_voice_settings_dict(voice_settings) if voice_settings else None,
        )  # type: ignore

        return url, data
