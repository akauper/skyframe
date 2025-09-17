from typing import Optional

from pydantic_settings import BaseSettings


class ClassifierSettings(BaseSettings):
    transformer_name: Optional[str] = None
    transformer_task: Optional[str] = None
    use_gpu: Optional[bool] = None
