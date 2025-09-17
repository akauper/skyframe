from typing import List, Dict, Any, Set


def find_nonexistent_keys(keys: List[str], data: Dict[str, Any]) -> Set[str]:
    key_set = set(keys)
    return {key for key in data if key not in key_set}


def change_key(data: Dict[str, Any], old_key: str, new_key: str) -> None:
    """
    Change the key of a dictionary from old_key to new_key and delete old_key.
    """
    if old_key in data:
        if new_key in data:
            raise ValueError(f"Cannot change key from {old_key} to {new_key} as {new_key} already exists")
        data[new_key] = data.pop(old_key)