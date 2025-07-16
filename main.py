from arg import Arg
from install import download_package_folder, run_install_script_from_cache
from init import run_init_command
from okgman_parser import build, clean  # builder/parser modülünden build & clean fonksiyonları
import subprocess
import os


def install_cmd(args):
    name = args.get("name")
    version = args.get("version", "latest")
    force = args.get("force", False)
    pos = args.get("_positional", [])

    if not name and pos:
        name = pos[0]

    if not name:
        print("[!] Package name is required.")
        return

    print(f"Installing package '{name}' version '{version}'")
    if force:
        print("Force install enabled.")
    # burada indirme, kurulum fonksiyonları çağırılabilir


def build_cmd(args):
    build()



def clean_cmd(args):
    clean()

def rebuild(args):
    clean()
    build()

if __name__ == "__main__":
    cli = Arg("pkgman", "Simple Python package manager")

    cli.add_command(
        "install",
        "Install a package",
        install_cmd,
        aliases=["i", "--install"],
        args_spec={
            "name": {"type": str, "required": True, "desc": "Package name"},
            "version": {"type": str, "required": False, "default": "latest", "desc": "Package version"},
            "force": {"type": bool, "required": False, "alias": ["-f"], "desc": "Force install"},
        }
    )

    cli.add_command(
        "init",
        "Initialize a new C project",
        run_init_command,
        aliases=["--init"],
        args_spec={
            "name": {"type": str, "required": False, "desc": "Project name"},
        }
    )

    cli.add_command(
        "build",
        "Build the project",
        build_cmd,
        aliases=["b"]
    )


    cli.add_command(
        "clean",
        "Clean build directory",
        clean_cmd,
        aliases=["c"]
    )

    cli.add_command(
        "rebuild",
        "Rebuild the project",
        rebuild,
        aliases=["rb"]
    )

    cli.parse()
