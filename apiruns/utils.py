import yaml
from pathlib import Path

def load_yaml(path_file: str):
    """Load yaml file.

    Args:
        path_file (str): Path file.
    """
    filename = Path(path_file).resolve()
    yaml_file = open(str(filename), "r")
    return yaml.load(yaml_file, yaml.Loader)
