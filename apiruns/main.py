import typer
from apiruns import __version__ as package_version
from .services import Apiruns


app = typer.Typer(add_completion=False)


@app.command()
def version():
    """Get current version. 💬"""
    typer.echo(package_version)


@app.command()
def build(
    file: str = typer.Option(
        ...,
        help="File configuration.",
    )
):
    """Build a API rest. 🚀"""
    Apiruns.build(file)
