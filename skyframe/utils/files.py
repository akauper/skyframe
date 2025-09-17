import pathlib


def get_framework_path() -> pathlib.Path:
    """Get the path of the framework directory.

    Returns:
        str: path of the framework directory.
    """
    return pathlib.Path(__file__).parent.parent.absolute()


def get_framework_data_path() -> pathlib.Path:
    """Get the path of the data directory in the framework.

    Returns:
        str: path of the data directory in the framework.
    """
    return get_framework_path() / "data"


def get_parent_dir_path(file_name: str) -> str:
    """Get the path of the parent directory of a file in the project.

    Args:
        file_name (str): name of the file.

    Returns:
        str: path of the parent directory of the file.
    """
    return str(pathlib.Path(__file__).parent.absolute())


def get_file_path(file_name: str) -> str:
    """Get the path of a file in the project.

    Args:
        file_name (str): name of the file.

    Returns:
        str: path of the file.
    """
    return str(pathlib.Path(__file__).parent.absolute()) + "/" + file_name


def get_file_content(file_name: str) -> str:
    """Get the content of a file in the project.

    Args:
        file_name (str): name of the file.

    Returns:
        str: content of the file.
    """
    with open(get_file_path(file_name)) as f:
        return f.read()


def get_project_path() -> pathlib.Path:
    """Get the path of the project.

    Returns:
        pathlib.Path: path of the project.
    """
    return pathlib.Path(__file__).parent.parent.parent.absolute()


def get_project_path_str() -> str:
    """Get the path of the project.

    Returns:
        str: path of the project.
    """
    return str(get_project_path())


def get_data_path() -> pathlib.Path:
    """Get the path of the data directory.

    Returns:
        pathlib.Path: path of the data directory.
    """
    return get_project_path() / "data"


def get_data_path_str() -> str:
    """Get the path of the data directory.

    Returns:
        str: path of the data directory.
    """
    return str(get_data_path())