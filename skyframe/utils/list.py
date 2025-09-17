from typing import List, TypeVar, Dict

_T = TypeVar("_T")


def get_duplicates(input_list: List[_T]) -> List[_T]:
    """Get the duplicates from a list."""
    counts = {}
    duplicates = []
    for item in input_list:
        counts[item] = counts.get(item, 0) + 1
        if counts[item] == 2:
            duplicates.append(item)
    return duplicates


def get_duplicate_counts(input_list: List[_T]) -> Dict[_T, int]:
    seen = set()
    duplicates: Dict[_T, int] = {}

    for item in input_list:
        if item in seen:
            duplicates[item] = duplicates.get(item, 1) + 1
        else:
            seen.add(item)

    return duplicates


def has_index(input_list: List[_T], index: int) -> bool:
    """Check if a list has a specific index."""
    return 0 <= index < len(input_list)
