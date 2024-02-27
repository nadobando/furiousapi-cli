import typer


def dict_from_args(ctx: typer.Context) -> dict[str, str]:
    return {
        k.lstrip('--'): ctx.args[i + 1] if not (i + 1 >= len(ctx.args) or ctx.args[i + 1].startswith('--')) else True
        for
        i, k
        in enumerate(ctx.args) if k.startswith('--')}
