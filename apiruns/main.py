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
        help="Apiruns configuration file.",
    ),
    version: Optional[str] = None
):
    """Build images & validate schema. 🔧"""
    Apiruns.build(file, version)


@app.command()
def up(
    file: Optional[str] = typer.Option(
        "apiruns-compose.yml",
        help="Apiruns configuration file.",
    )
):
    """Make your API rest. 🚀"""
    Apiruns.up(file)


@app.command()
def down(
    file: Optional[str] = typer.Option(
        "apiruns-compose.yml",
        help="Apiruns configuration file.",
    )
):
    """Stops containers and removes containers. 🌪"""
    Apiruns.down(file)
