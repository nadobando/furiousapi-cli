import typer

from furiousapi.cli.generate import typer_app as generate
from furiousapi.cli.postman import typer_app as postman

app = typer.Typer(name="FuriousAPI-CLI")
app.add_typer(generate)
app.add_typer(postman)

app()