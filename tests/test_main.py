from unittest.mock import patch
from apiruns.main import version
from apiruns.main import build
from apiruns.main import up
from apiruns.main import down
from apiruns import __version__


@patch("apiruns.main.typer.echo")
def test_version(echo_mock):
    version()

    # Asserts
    echo_mock.assert_called_once_with(__version__)


@patch("apiruns.main.Apiruns.build")
def test_build(service_mock):
    build(file="myapi.yml", version="1.0.1")

    # Asserts
    service_mock.assert_called_once_with("myapi.yml", "1.0.1")


@patch("apiruns.main.Apiruns.up")
def test_up(service_mock):
    up(file="myapi.yml")

    # Asserts
    service_mock.assert_called_once_with("myapi.yml")


@patch("apiruns.main.Apiruns.down")
def test_down(service_mock):
    down(file="myapi.yml")

    # Asserts
    service_mock.assert_called_once_with("myapi.yml")
