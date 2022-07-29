from typing import Any
import yaml
import json
import urllib.parse
from pathlib import Path

def load_yaml(path_file: str):
    """Load yaml file.

    Args:
        path_file (str): Path file.
    """
    filename = Path(path_file).resolve()
    yaml_file = open(str(filename), "r")
    return yaml.load(yaml_file, yaml.Loader)


def encode_obj_to_url(obj: Any) -> str:
    """Encode object to url string.

    Args:
        obj (Any): Object to encode.

    Returns:
        str: url string
    """
    return urllib.parse.quote(json.dumps(obj))
