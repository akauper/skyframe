import base64
import os
import re
import tempfile
from typing import Optional, Union, TextIO, BinaryIO, Literal

import ffmpeg


def audio_file_to_wav(input_file_path: str, output_file_path: str):
    try:
        (
            ffmpeg
            .input(input_file_path)
            .output(output_file_path, format='wav')
            .run(overwrite_output=True, quiet=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr)  # This will print the error from FFmpeg
        raise


FDMode = Literal["r+", "+r", "rt+", "r+t", "+rt", "tr+", "t+r", "+tr", "w+", "+w", "wt+", "w+t", "+wt", "tw+", "t+w", "+tw", "a+", "+a", "at+", "a+t", "+at", "ta+", "t+a", "+ta", "x+", "+x", "xt+", "x+t", "+xt", "tx+", "t+x", "+tx", "w", "wt", "tw", "a", "at", "ta", "x", "xt", "tx", "r", "rt", "tr", "U", "rU", "Ur", "rtU", "rUt", "Urt", "trU", "tUr", "Utr"]


class CustomTempFile:
    """
    A context manager for creating and handling a temporary file.
    """
    mode: FDMode
    suffix: Optional[str]
    delete: bool
    temp_file_path: Optional[str]
    file: Optional[Union[TextIO, BinaryIO]]

    def __init__(
            self,
            *,
            mode: FDMode = 'wb',
            suffix: Optional[str] = None,
            delete: bool = True,
    ):
        self.mode = mode
        self.suffix = suffix
        self.delete = delete
        self.temp_file_path = None
        self.file = None

    def __enter__(self) -> BinaryIO:
        fd, self.temp_file_path = tempfile.mkstemp(suffix=self.suffix)
        self.file = os.fdopen(fd, self.mode)
        return self.file

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[object]) -> None:
        if self.file:
            self.file.close()
        if self.delete and self.temp_file_path:
            os.remove(self.temp_file_path)


class CreateWavFile:
    """
    A class to convert audio file paths, base64 encoded strings, or bytes to .wav format.
    """

    base64_pattern = r'^[A-Za-z0-9+/]*={0,2}$'

    file_path: str
    is_temporary_file: bool

    def __init__(
            self,
            data_or_file: Union[str, bytes],
            *,
            mime_type: Optional[str] = None,
    ) -> None:

        data: bytes

        if isinstance(data_or_file, str):
            # First we check if we already have a file path.
            if os.path.exists(data_or_file):
                extension = os.path.splitext(self.file_path)[1]
                if extension != '.wav':
                    self.file_path = data_or_file.replace(extension, '.wav')
                    audio_file_to_wav(data_or_file, self.file_path)
                    self.is_temporary_file = True
                else:
                    self.is_temporary_file = False
                return
            # otherwise we ensure that the string is base64 encoded.
            elif re.match(self.base64_pattern, data_or_file):
                data = base64.b64decode(data_or_file)
            else:
                raise ValueError(f'Unsupported data type: {type(data_or_file)} -- Not a file path or base64 string')
        elif isinstance(data_or_file, bytes):
            data = data_or_file
        else:
            raise ValueError(f'Unsupported data type: {type(data_or_file)} -- Not a file path or base64 string')

        # We have data, now get the extension.
        if mime_type is not None:
            extension = mime_type.split('/')[1]
            if ';' in extension:
                extension = extension.split(';')[0]
            extension = f'.{extension}'
        else:
            extension = '.wav'

        # Now we create a temporary file and write the data to it.
        fd, t_path = tempfile.mkstemp(suffix=extension)
        file = os.fdopen(fd, 'wb')
        file.write(data)
        file.flush()
        file.close()

        # Now we convert the file to .wav if necessary.
        if extension != '.wav':
            self.file_path = t_path.replace(extension, '.wav')
            audio_file_to_wav(t_path, self.file_path)
            os.remove(t_path)
        else:
            self.file_path = t_path

        self.is_temporary_file = True

    def __enter__(self):
        return self.file_path

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[object]) -> None:
        if self.is_temporary_file and os.path.exists(self.file_path):
            os.remove(self.file_path)
