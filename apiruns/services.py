from .serializers import FileSerializer
from rich import print
import typer

class Apiruns:

    @classmethod
    def build(cls, path_file: str, up: bool = False):
        api_name, data_schema = FileSerializer.read_file(path_file)
        FileSerializer.validate(data_schema)
        typer.echo("Building API")
        print(data_schema)
