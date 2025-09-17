from typing import Dict, Any, Optional

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class BaseRunnableSettings(BaseSettings):
    metadata: Optional[Dict[str, Any]] = None
    verbose: Optional[bool] = None

    model_config = ConfigDict(
        extra='allow',
    )
