from typing import List, Union


def weighted_average(values: List[Union[int, float]], weights: List[Union[int, float]]) -> float:
    if len(values) != len(weights):
        raise ValueError("The number of values and weights must be the same.")

    weighted_sum = sum(value * weight for value, weight in zip(values, weights))
    total_weight = sum(weights)

    if total_weight == 0:
        raise ValueError("The sum of weights must be non-zero.")

    return weighted_sum / total_weight
