from unittest.mock import patch, call
from apiruns.services import Apiruns


class TestApiruns:

    data = [
        {
            "path": "/users",
            "schema": {
                "name": {"type": "string"}
            }
        }
    ]

    @patch("apiruns.services.typer.echo")
    @patch("apiruns.services.FileSerializer.validate")
    @patch("apiruns.services.DockerClient.compose_service")
    @patch("apiruns.services.FileSerializer.read_file")
    def test_build_success(self, read_file_mock, compose_mock, validator_mock, typer_mock):
        read_file_mock.return_value = "my_api", self.data
        Apiruns.build("mifile.yml")

        # asserts
        read_file_mock.assert_called_with("mifile.yml")
        compose_mock.assert_called_with('my_api', start=False)
        validator_mock.assert_called_with(self.data)
        calls = [call("Building API"), call("Services made.")]
        typer_mock.assert_has_calls(calls, any_order=False)


    @patch("apiruns.services.APIClient")
    @patch("apiruns.services.typer.echo")
    @patch("apiruns.services.FileSerializer.validate")
    @patch("apiruns.services.DockerClient.compose_service")
    @patch("apiruns.services.FileSerializer.read_file")
    def test_up_success(self, read_file_mock, compose_mock, validator_mock, typer_mock, client_mock):
        read_file_mock.return_value = "my_api", self.data
        Apiruns.up("mifile.yml")

        # asserts
        read_file_mock.assert_called_with("mifile.yml")
        compose_mock.assert_called_with('my_api', start=True)
        validator_mock.assert_called_with(self.data)
        calls = [call("Building API"), call("Starting services"), call("API listen on 8000")]
        typer_mock.assert_has_calls(calls, any_order=False)
        client_mock.ping.assert_called_with()
        client_mock.create_models.assert_called_with(self.data)


    @patch("apiruns.services.DockerClient.service_down")
    @patch("apiruns.services.FileSerializer.read_file")
    def test_down_success(self, read_file_mock, compose_mock):
        read_file_mock.return_value = "my_api", self.data
        Apiruns.down("mifile.yml")

        # asserts
        read_file_mock.assert_called_with("mifile.yml")
        compose_mock.assert_called_with("my_api")
