import asyncio
from pathlib import Path
from typing import Tuple

from pydantic import Field

from skyframe.utils import get_project_path_str
from ..base import Runnable


class TransformersQueryClassifier(Runnable):

    transformer_name: str = Field(default='deberta-v3-base-prompt-injection')
    transformer_task: str = Field(default='text-classification')
    use_gpu: bool = Field(default=False)

    async def run_async(self, query: str) -> Tuple[str, float]:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
        import torch

        model_path = Path(get_project_path_str()) / "transformer_models" / "models" / self.transformer_name

        tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)

        classifier = pipeline(
            self.transformer_task,
            model=model,
            tokenizer=tokenizer,
            truncation=True,
            max_length=512,
            device=torch.device("cuda" if self.use_gpu and torch.cuda.is_available() else "cpu"),
        )

        def classify_sync():
            return classifier(query)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, classify_sync)

        classification = result[0]
        return classification['label'], classification['score']
