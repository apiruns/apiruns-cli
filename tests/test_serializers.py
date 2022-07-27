import pytest
from unittest.mock import patch
from apiruns.serializers import SerializerBase
from apiruns.serializers import FileSerializer
from apiruns.exceptions import ErrorReadingFile
from apiruns.exceptions import ErrorValidatingSchema


def test_call_without_error_serializer_base():
    schema = {
        "name": {
            "type": "string"
        },
        "age": {
            "type": "integer"
        }
    }

    data = {
        "name": "test",
        "age": 78,
    }

    resp = SerializerBase._validate(schema=schema, data=data)
    assert resp == {}


def test_call_with_error_serializer_base():
    schema = {
        "name": {
            "type": "string"
        },
        "age": {
            "type": "integer"
        }
    }

    data = {
        "name": True
    }

    resp = SerializerBase._validate(schema=schema, data=data)
    assert resp == {'name': ['must be of string type']}


@patch("apiruns.serializers.load_yaml")
def test_read_file_with_no_data(load_yaml_mock):
    load_yaml_mock.return_value = {}
    with pytest.raises(ErrorReadingFile):
        FileSerializer.read_file("file.yml")


@patch("apiruns.serializers.load_yaml")
def test_read_file_with_data(load_yaml_mock):
    data = {
        "my_api": [
            {
                "path": "/users",
                "schema": {
                    "name": {"type": "string"}
                }
            }
        ]
    }
    load_yaml_mock.return_value = data
    name, schemas = FileSerializer.read_file("file.yml")
    assert name == "my_api"
    assert schemas == data["my_api"]

def test_validate_list_of_schema_with_error():
    data = [
            {
                "schema": {
                    "name": {"type": "string"}
                }
            }
        ]
    with pytest.raises(ErrorValidatingSchema):
        FileSerializer.validate(data)

def test_validate_list_of_schema():
    data = [
            {
                "path": "/users",
                "schema": {
                    "name": {"type": "string"}
                }
            }
        ]
    FileSerializer.validate(data)
