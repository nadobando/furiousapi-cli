import importlib
import json
import os
import subprocess
import sys
from importlib.resources import files

import typer
from fastapi import FastAPI

from furiousapi.cli.postman.utils import _recursive_remove_datetime_format

typer_app = typer.Typer(name="postman")

PORTMAN_OPEN_API_FILE_NAME = "./openapi.portman.json"


def _preprocess(app):
    is_uncommitted = subprocess.run("git diff-index --quiet HEAD --", shell=True, check=False).returncode != 0

    version = subprocess.check_output("git rev-parse --short HEAD", shell=True).strip().decode()  # nosec: B607,B602
    if is_uncommitted:
        version += "not-synced"
    schema = app.openapi()

    _recursive_remove_datetime_format(schema)

    with open(PORTMAN_OPEN_API_FILE_NAME, "w") as f:
        json.dump(schema, f, indent=2)


def _postprocess():
    os.remove(PORTMAN_OPEN_API_FILE_NAME)


@typer_app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def collection(ctx: typer.Context, app_path: str):
    portman_args = "--local ../openapi.portman.json "

    if not ctx.args:
        portman_cli = files("furiousapi").joinpath("cli/postman/postman-convert-config.json")
        portman_args += (
            f"--postmanConfigFile {portman_cli} --output {os.path.join(os.getcwd(), 'postman-collection.json')}"
        )
    else:
        portman_args += " ".join(ctx.args)

    app = _import_module(app_path)
    _preprocess(app)

    try:
        npm = (
            subprocess.check_output("which npm", stderr=subprocess.STDOUT, shell=True)  # nosec: B607,B602
            .strip()
            .decode()
        )
        portman_installed = subprocess.run(  # nosec: B607,B602
            f"{npm} list | grep portman", check=False, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True
        )

        if portman_installed.returncode > 0:
            sys.stderr.write("you must install portman, `npm install @apideck/portman`")
            exit(1)

        npm_root = (
            subprocess.check_output(  # nosec: B603
                [npm, "root"],
                stderr=subprocess.STDOUT,
            )
            .strip()
            .decode("utf-8")
        )
        # --postmanConfigFile
        portman_bin = f"{npm_root}/.bin/portman"
        # portman_config = "../../postman/portman-cli.json"
        # portman_args = f"--cliOptionsFile {portman_config} --output {output_file}"
        create_tmp_portman_dir_cmd = "mkdir .portman 2>/dev/null || true && cd .portman"
        portman_cmd = f"{portman_bin} {portman_args}"
        delete_tmp_portman_dir_cmd = "rm -rf ../.portman"
        cmd = f"{create_tmp_portman_dir_cmd} && {portman_cmd};{delete_tmp_portman_dir_cmd}"
        # print(cmd)
        # print(os.path.exists(portman_config))
        result = subprocess.check_output(
            cmd,
            shell=True,  # nosec: B602
            stderr=subprocess.STDOUT,
        )
        print(result.decode("utf-8"))
    except subprocess.CalledProcessError as e:
        print(e)
        print(e.cmd)
        print(e.output.decode("utf-8"))
    finally:
        _postprocess()


def _import_module(app_path: str) -> FastAPI:
    module_period, _, obj = app_path.rpartition(":")
    module_path = module_period.replace(".", os.path.sep)
    p = os.path.join(os.getcwd(), module_path.rpartition("/")[0])
    sys.path = sys.path + [p]
    module = importlib.import_module(module_period)
    app = getattr(module, obj)
    return app
