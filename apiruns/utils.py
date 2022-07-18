import yaml
from pathlib import Path

def load_yaml(path_file: str):
    """Load yaml file.

    Args:
        path_file (str): Path file.
    """
    path_file = f"../{path_file}"
    path = (Path(__file__).parent / path_file).resolve()
    yaml_file = open(path, "r")
    return yaml.load(yaml_file, yaml.Loader)
