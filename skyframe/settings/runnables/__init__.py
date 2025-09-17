from pydantic import Field
from pydantic_settings import BaseSettings

from .agents import AgentSettings
from .classifiers import ClassifierSettings
from .post_processors import PostProcessorSettings
from .generators import GeneratorSettings


class RunnableSettings(BaseSettings):
    agents: AgentSettings = Field(default_factory=AgentSettings)
    classifiers: ClassifierSettings = Field(default_factory=ClassifierSettings)
    post_processors: PostProcessorSettings = Field(default_factory=PostProcessorSettings)
    generators: GeneratorSettings = Field(default_factory=GeneratorSettings)
