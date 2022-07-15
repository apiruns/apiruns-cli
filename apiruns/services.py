from .serializers import FileSerializer
from .clients import DockerClient
from .clients import APIClient
from rich import print
import typer

class Apiruns:

    @classmethod
    def build(cls, file_path: str, up: bool = False):
        """Command to build the services.

        Args:
            file_path (str): Relative file path.
            up (bool, optional): If up?. Defaults to False.
        """
        api_name, data_schema = FileSerializer.read_file(file_path)
        FileSerializer.validate(data_schema)
        typer.echo("Building API")
        DockerClient.compose_service(api_name)
        typer.echo("Starting services")
        #APIClient.ping()
        #APIClient.create_models(data_schema)
        print("API listen on 8000")
