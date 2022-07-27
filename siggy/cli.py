from pathlib import Path
import json
import os

import click

from siggy.update import execute

SIGGYRC_PATH = Path(os.environ["HOME"], ".siggyrc").absolute()

siggy_config = {}
if SIGGYRC_PATH.exists():
    with SIGGYRC_PATH.open() as file:
        siggy_config = json.load(file)


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        if siggy_config:
            execute(
                siggy_config.get("name"),
                siggy_config.get("role"),
                siggy_config.get("phone"),
            )
        else:
            click.echo("Missing config. Please run `siggy config` first.")


@cli.command()
@click.option("--name", prompt=True, default=siggy_config.get("name"))
@click.option("--role", prompt=True, default=siggy_config.get("role"))
@click.option("--phone", prompt=True, default=siggy_config.get("phone"))
def config(name, role, phone):
    with SIGGYRC_PATH.open("w+") as file:
        json.dump(
            {
                "name": name,
                "role": role,
                "phone": phone,
            },
            file,
        )


if __name__ == "__main__":
    cli()
