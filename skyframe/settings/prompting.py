from pydantic import Field
from pydantic_settings import BaseSettings


class PromptingSettings(BaseSettings):
    data_dir: str = Field(default='./data/prompting',
                          description='The relative path (from settings.yaml) to the data directory for prompts.')

    # model_config = SettingsConfigDict(env_prefix='PROMPTING_', env_file='.env')
