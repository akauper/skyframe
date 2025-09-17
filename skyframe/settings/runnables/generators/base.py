from typing import Any, Dict, Optional

from ..base import BaseRunnableSettings


class BaseGeneratorSettings(BaseRunnableSettings):
    enabled: bool = True
    service_name: Optional[str] = None
    generation_params: Optional[Dict[str, Any]] = None
    services: Optional[Dict[str, Any]] = None

    def get_service_value(self, *keys: str) -> Any:
        if self.services is None:
            return None

        value = self.services
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None

        return value
