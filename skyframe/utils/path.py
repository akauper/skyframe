from pathlib import Path


def find_project_root():
    current_dir = Path.cwd()
    for parent in current_dir.parents:
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            return parent
    return current_dir
