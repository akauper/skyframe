from pydantic_settings import BaseSettings


class LoggingSettings(BaseSettings):
    base_log_level: str = 'INFO'
    log_to_file: bool = False
