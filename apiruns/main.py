import typer
from apiruns import __version__ as package_version


app = typer.Typer(add_completion=False)

@app.command()
def version():
    """Get current version."""
    typer.echo(package_version)

@app.command()
def build():
    """Build API"""
    typer.echo("Building API")
