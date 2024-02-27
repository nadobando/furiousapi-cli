from enum import Enum
from pathlib import Path

import typer
from jinja2 import Environment, PackageLoader
from rich.console import Console
import inflect
from . import utils

typer_app = typer.Typer(name="create")

env = Environment(
    loader=PackageLoader("furiousapi.cli.generate"), lstrip_blocks=True, trim_blocks=True, autoescape=True
)
engine = inflect.engine()
env.filters["pluralize"] = engine.plural_noun
console = Console()


class PersistenceStores(str, Enum):
    MONGODB = "mongo"
    SQL = "sql"


@typer_app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def app(name: str, ctx: typer.Context, source: PersistenceStores = PersistenceStores.SQL) -> None:
    templates = env.list_templates(extensions=["jinja2"])
    app_title = engine.singular_noun(name.title())

    cwd = Path.cwd()
    app_path = cwd.joinpath(name)
    console.print(f"Rendering {app_title} to {app_path}", style="magenta")
    for template in templates:
        rendered = env.get_template(template).render(
            *ctx.args,
            source=source.value,
            app_name=app_title,
        )
        real_name = template.replace("{{app_name}}", name)
        Path(app_path).mkdir(parents=True, exist_ok=True)

        file_path = cwd.joinpath(real_name.replace(".jinja2", ""))
        with file_path.open("w+") as _f:
            _f.write(rendered)

    utils.print_tree(str(app_path))
