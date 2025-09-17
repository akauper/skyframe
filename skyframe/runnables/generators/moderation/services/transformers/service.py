import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

from skyframe.utils import logger, get_project_path_str
from .converter import TransformersModerationConverter
from ..base import BaseModerationService
from ...models import ModerationResponse, ModerationGenerationParams


class TransformersModerationService(BaseModerationService):
    converter: TransformersModerationConverter
    default_model: str = 'deberta-v3-base-prompt-injection'

    def __init__(self):
        super().__init__()
        self.converter = TransformersModerationConverter()

    def run(
            self,
            request: str,
            generation_params: ModerationGenerationParams
    ) -> ModerationResponse:
        if request is None:
            raise ValueError('ModerationRequest cannot be None')

        model_path = Path(get_project_path_str()) / "transformer_models" / "models" / self.default_model

        transformer_response = self._classify_sync(request, str(model_path))

        logger.dev_debug(transformer_response)

        response = self.converter.from_transformer_response(self.default_model, transformer_response)

        logger.dev_debug(response)

        return response

    async def run_async(
            self,
            request: str,
            generation_params: ModerationGenerationParams
    ) -> ModerationResponse:
        if request is None:
            raise ValueError('ModerationRequest cannot be None')

        model_path = Path(get_project_path_str()) / "transformer_models" / "models" / self.default_model

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            transformer_response = await loop.run_in_executor(executor, self._classify_sync, request, str(model_path))

        logger.dev_debug(transformer_response)

        response = self.converter.from_transformer_response(self.default_model, transformer_response)

        logger.dev_debug(response)

        return response

    @staticmethod
    def _classify_sync(query: str, model_path: str) -> List:
        tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)

        classifier = pipeline(
            'text-classification',
            model=model,
            tokenizer=tokenizer,
            truncation=True,
            max_length=512,
            #device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
            device=torch.device("cpu"),
        )

        result = classifier(query)

        return result