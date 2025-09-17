from typing import Optional

from .base import FrameworkException


class GenerationException(FrameworkException):
    message: str
    inner_exception: Optional[Exception] = None

    def __init__(
            self,
            *,
            message: str,
            inner_exception: Optional[Exception] = None,
    ):
        self.message = message
        self.inner_exception = inner_exception
        super().__init__(message)