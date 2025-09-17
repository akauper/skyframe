import asyncio
from typing import List

import yaml
from devtools import debug
from pydantic import BaseModel, Field

from skyframe.utils import logger, get_data_path
from .evaluator_options import EvaluatorOptions
from .resolvables.evaluation import Evaluation
from .evaluation_summary import EvaluationSummary


class Evaluator(BaseModel):
    """
    Evaluates an evaluation against a model and generates a summary of the results.

    Attributes:
        evaluation (Evaluation): The evaluation to run.
        options (EvaluatorOptions): The options for the evaluator.
    """

    evaluation: Evaluation
    """The evaluation to run"""

    options: EvaluatorOptions = Field(default_factory=EvaluatorOptions)

    async def evaluate_async(self) -> EvaluationSummary:
        """
        Runs the evaluation asynchronously.

        Returns:
            EvaluationSummary: A summary of the evaluation results.
        """

        logger.info(f"Running evaluation: {self.evaluation.name}")

        concurrency = self.options.max_concurrent_requests
        if concurrency == 0:
            concurrency = 999

        semaphore = asyncio.Semaphore(concurrency)

        result = await self.evaluation.resolve_async(semaphore)

        summary = EvaluationSummary(
            name=self.evaluation.name,
            evaluation=self.evaluation,
            evaluation_result=result
        )

        self._save_summary(summary)

        return summary

    @staticmethod
    def _save_summary(summary: EvaluationSummary):
        """
        Saves the EvaluationResult to a file.
        """
        debug(summary.model_dump_json(indent=4))
        path = get_data_path() / "evaluation" / "results" / f"{summary.name if summary.name else ''}-{summary.id}.json"
        logger.info(f"Saving evaluation summary to file: {path}")
        path.write_text(summary.model_dump_json(indent=4), encoding='utf-8')

    @classmethod
    def load(cls, file_path: str, relative: bool = True) -> List['Evaluator']:
        logger.info(f"Loading evaluator from file: {file_path}")
        if relative:
            path = get_data_path() / "evaluation" / "tests" / file_path
        else:
            path = file_path
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        if "tests" in data:
            # If we have a single eval convert it to a keyed eval.
            data = {path.stem: data}

        evaluators: List['Evaluator'] = []
        for key in data:
            evaluation_dict = data[key]
            if "name" not in evaluation_dict:
                evaluation_dict["name"] = key
            evaluation = Evaluation.model_validate(evaluation_dict)
            evaluators.append(cls(evaluation=evaluation))
        return evaluators
