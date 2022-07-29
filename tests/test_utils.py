import pytest
import yaml
from apiruns.utils import load_yaml
from apiruns.utils import encode_obj_to_url
from unittest.mock import patch, mock_open

def test_file_not_found_load_yaml():
    with pytest.raises(FileNotFoundError):
        load_yaml("mifile.yml")

def test_success_load_yaml():
    with patch("builtins.open", mock_open(read_data="data")) as mock_file:
        mock_file.return_value = """service_name: myproject"""
        resp = load_yaml("mifile.yml")
        assert resp == {'service_name': 'myproject'}

def test_encode_obj_to_url():
    resp = encode_obj_to_url({"status": ["paused"]})
    assert resp == "%7B%22status%22%3A%20%5B%22paused%22%5D%7D"
