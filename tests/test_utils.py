import pytest
import yaml
from apiruns.utils import load_yaml
from unittest.mock import patch, mock_open

def test_file_not_found_load_yaml():
    with pytest.raises(FileNotFoundError):
        load_yaml("mifile.yml")

def test_success_load_yaml():
    with patch("builtins.open", mock_open(read_data="data")) as mock_file:
        mock_file.return_value = """service_name: myproject"""
        resp = load_yaml("mifile.yml")
        assert resp == {'service_name': 'myproject'}
