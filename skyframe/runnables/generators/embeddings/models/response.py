from typing import Optional, List
from uuid import uuid4

from pydantic import BaseModel, Field

from skyframe.models import TokenUsage

import numpy as np


class EmbeddingsResponse(BaseModel):
    """
    Represents the response from an embeddings API.

    This class is what Quiply converts all embeddings responses from different services into.
    """

    id: str = Field(default=lambda: str(uuid4()))
    """A unique identifier for the completion."""

    data: List[List[float]]
    """A list of embedding vectors, which is a list of floats."""

    model: Optional[str] = Field(default=None)
    """The name of the model used to generate the embedding."""

    token_usage: Optional[TokenUsage]
    """Usage information for the completion. Token counts, etc."""

    @property
    def embedding(self) -> List[float]:
        """Returns the first (and usually only?) embedding vector."""
        return self.data[0]

    @property
    def embeddings(self) -> List[List[float]]:
        """Returns all the embedding vectors."""
        return self.data

    def compare_similarity(self, other: Optional['EmbeddingsResponse'] = None) -> float:
        """
        Compares the similarity between two embeddings.
        """
        if not other and len(self.data) < 2:
            raise ValueError("Cannot compare similarity between one embedding.")

        a = np.array(self.data[0])
        b = np.array(other.data[0] if other else self.data[1])

        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        cosine_similarity = dot_product / (norm_a * norm_b) if norm_a * norm_b > 0 else 0

        return cosine_similarity
