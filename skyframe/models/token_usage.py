from typing import List

from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    total: int = Field(default=0, ge=0)
    prompt: int = Field(default=0, ge=0)
    completion: int = Field(default=0, ge=0)

    total_cost: float = Field(default=0, ge=0)
    prompt_cost: float = Field(default=0, ge=0)
    completion_cost: float = Field(default=0, ge=0)

    def __add__(self, other: 'TokenUsage'):
        return TokenUsage(
            total=self.total + other.total,
            prompt=self.prompt + other.prompt,
            completion=self.completion + other.completion,

            total_cost=self.total_cost + other.total_cost,
            prompt_cost=self.prompt_cost + other.prompt_cost,
            completion_cost=self.completion_cost + other.completion_cost
        )

    def __iadd__(self, other: 'TokenUsage'):
        self.total += other.total
        self.prompt += other.prompt
        self.completion += other.completion

        self.total_cost += other.total_cost
        self.prompt_cost += other.prompt_cost
        self.completion_cost += other.completion_cost

        return self

    @classmethod
    def sum(cls, usages: List['TokenUsage']) -> 'TokenUsage':
        usage = cls()
        for u in usages:
            if u is None:
                continue
            usage += u
        return usage

    def calculate_cost(self, cost_per_input_token: float, cost_per_output_token: float):
        self.prompt_cost = self.prompt * cost_per_input_token
        self.completion_cost = self.completion * cost_per_output_token
        self.total_cost = self.prompt_cost + self.completion_cost
