
from typing import Tuple
from cerberus import Validator
from .utils import load_yaml
from .exceptions import ErrorReadingFile
from .exceptions import ErrorValidatingSchema

class SerializerBase:
    """Serialize Base"""

    @classmethod
    def _validate(cls, schema: dict, data: dict) -> dict:
        """Validate schema & data.

        Args:
            schema (dict): Cerberus schema.
            data (dict): Request data.

        Returns:
            dict: Errors.
        """
        v = Validator(schema, purge_unknown=False)
        v.validate(data)
        return v.errors


class FileSerializer(SerializerBase):
    """File serializer.

    Args:
        SerializerBase (SerializerBase): Base.

    Raises:
        ErrorReadingFile: Error reading file.
        ErrorValidatingSchema: Error validating schema.
    """

    FILE_SCHEMA = {
        "path": {
            "type": "string",
            "required": True,
            "empty": False,
            "minlength": 1,
            "regex": "^/|/[a-z0-9]+(?:/[a-z0-9]+|/)*$",
        },
        "name": {
            "type": "string",
            "maxlength": 70,
            "regex": "^[a-z0-9]+(?:-[a-z0-9]+)*$",
        },
        "schema": {"type": "dict", "required": True, "empty": False, "minlength": 1},
        "status_code": {
            "type": "dict",
            "required": False,
            "empty": False
        },
        "static": {
            "type": "dict",
            "required": False,
            "empty": False,
        },
    }

    @classmethod
    def read_file(cls, file_path: str) -> Tuple[str, dict]:
        """Read apiruns compose file.

        Args:
            file_path (str): Relative path.

        Raises:
            ErrorReadingFile: Error reading file.

        Returns:
            Tuple[str, dict]: _description_
        """
        data = load_yaml(file_path)
        if not data.keys():
            raise ErrorReadingFile

        data_schema = list(data.keys())
        api_name = data_schema[0]
        return api_name, data.get(api_name)

    @classmethod
    def validate(cls, data: list) -> None:
        """Validate data to save.

        Args:
            data (list): Data to save.

        Raises:
            ErrorValidatingSchema: Data isn't valid.
        """
        for d in data:
            errors = cls._validate(cls.FILE_SCHEMA, d)
            if errors:
                raise ErrorValidatingSchema(errors=errors)
