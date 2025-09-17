import inspect
import logging
import sys
from abc import ABC
from typing import TypeVar, Generic
import devtools
from skyframe.settings import framework_settings, LoggingSettings


TLoggingSettings = TypeVar('TLoggingSettings', bound=LoggingSettings)


class BaseSkyLogger(logging.Logger, ABC, Generic[TLoggingSettings]):
    def __init__(self, name: str, settings: TLoggingSettings):
        super().__init__(name)
        self.settings: TLoggingSettings = settings

        console_handler = logging.StreamHandler(stream=sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.addHandler(console_handler)

        if self.settings.log_to_file:
            file_handler = logging.FileHandler(f'{name}.log')
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.addHandler(file_handler)

    def is_debug(self) -> bool:
        return self.isEnabledFor(logging.DEBUG)

    def dev_debug(self, msg, **kwargs):
        if self.isEnabledFor(logging.DEBUG):
            # Extract the caller's stack frame
            frame = inspect.currentframe().f_back.f_back
            # Get the caller's file and line number
            filename = frame.f_code.co_filename

            devtools.debug(msg, **kwargs, frame_depth_=3)


class FrameworkLogger(BaseSkyLogger):
    def __init__(self):
        super().__init__('SKY_FRAMEWORK', framework_settings.logging)
        self.setLevel(self.settings.base_log_level.upper())


logger: FrameworkLogger = FrameworkLogger()
