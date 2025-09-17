import threading
from contextvars import ContextVar
from typing import Optional
from typing_extensions import TypedDict, Unpack


class EvaluationContextSettings(TypedDict, total=False):
    key: str
    index: int
    run_id: Optional[str]


def _from_default_settings(settings: EvaluationContextSettings) -> EvaluationContextSettings:
    return {
        "key": settings.get("key", "default"),
        "index": settings.get("index", 0),
        "run_id": settings.get("run_id", None)
    }


class EvaluationContext:
    # Thread-local storage for synchronous contexts
    _thread_local = threading.local()
    # Context variable for asynchronous contexts
    _context_settings: ContextVar[Optional[EvaluationContextSettings]] = ContextVar('context_settings', default=None)

    def __init__(self, **settings: Unpack[EvaluationContextSettings]):
        self.settings: EvaluationContextSettings = _from_default_settings(settings)
        self._token = None

    def __enter__(self):
        # Store settings in thread-local storage for synchronous code
        self._thread_local.settings = self.settings
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clear thread-local storage when exiting synchronous context
        self._thread_local.settings = None

    async def __aenter__(self):
        # Store settings in context variable for asynchronous code
        self._token = self._context_settings.set(self.settings)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Reset context variable when exiting asynchronous context
        self._context_settings.reset(self._token)

    @classmethod
    def get_current_settings(cls) -> Optional[EvaluationContextSettings]:
        # Try to get settings from asynchronous context first
        async_settings = cls._context_settings.get()
        if async_settings is not None:
            return async_settings
        # Fallback to thread-local storage for synchronous code
        return getattr(cls._thread_local, 'settings', None)


# class EvaluationContext:
#     _thread_local = threading.local()
#     settings: Union[EvaluationContextSettings, None]
#
#     def __init__(self, **settings):
#         self.settings = EvaluationContextSettings.model_validate(settings)
#
#     def __enter__(self):
#         # Store the current context in thread-local storage
#         self._thread_local.settings = self.settings
#         return self
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         # Restore the old context settings when exiting the context
#         self._thread_local.settings = None
#
#     @classmethod
#     def get_current_settings(cls) -> Optional[EvaluationContextSettings]:
#         # Method to access the current context settings
#         return getattr(cls._thread_local, 'settings', None)
#
#
# class AsyncEvaluationContext:
#     _context_settings: ContextVar[Optional[EvaluationContextSettings]] = ContextVar('context_settings', default=None)
#
#     def __init__(self, **settings):
#         self.settings = EvaluationContextSettings.model_validate(settings)
#         self._token = None
#
#     async def __aenter__(self):
#         self._token = self._context_settings.set(self.settings)
#         return self
#
#     async def __aexit__(self, exc_type, exc_val, exc_tb):
#         self._context_settings.reset(self._token)
#
#     @classmethod
#     def get_current_settings(cls) -> Optional[EvaluationContextSettings]:
#         return cls._context_settings.get()
