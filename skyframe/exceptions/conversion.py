from typing import Type, Optional

from .base import FrameworkException


class ConversionException(FrameworkException):
    convertor_type: Type
    from_type: Type
    to_type: Type
    inner_exception: Optional[Exception]

    def __init__(
        self,
        convertor_type: Type,
        *,
        from_type: Type,
        to_type: Type,
        inner_exception: Optional[Exception] = None,
    ):
        self.convertor_type = convertor_type
        self.from_type = from_type
        self.to_type = to_type
        self.inner_exception = inner_exception
        super().__init__()
