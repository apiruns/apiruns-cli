from typing import Optional
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
    file: Optional[str] = typer.Option(
        "apiruns-compose.yml",
        help="File configuration.",
    )
):
    """Build a API rest. 🚀"""
    Apiruns.build(file)
