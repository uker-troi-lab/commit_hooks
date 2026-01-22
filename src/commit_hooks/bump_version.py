import subprocess
from sys import stdout
import os
import sys
import tempfile
import tomllib
import subprocess

system_tempdir = tempfile.gettempdir()
msg_helper_file = os.path.join(system_tempdir, ".commit_msg.txt")

pardir = os.path.dirname(os.path.abspath(__file__))
bump_config_file = os.path.join(pardir, "configs", "bump_version.toml")

print_prefix = "[bump-version]:"


def bump_version():
    print(f"{print_prefix} config file: {bump_config_file}")

    # open pyproject toml from repo's root dir
    with open("pyproject.toml", "rb") as f:
        toml_dict = tomllib.load(f)
    current_version = toml_dict["project"]["version"]
    if len(current_version) == "":
        print(f"{print_prefix} failed to extract current version")
        sys.exit(1)
    else:
        print(
            f"{print_prefix} extracted current version '{current_version}' from pyproject.toml"
        )

    os.environ["BUMPVERSION_CURRENT_VERSION"] = current_version

    base_command = f"--config-file {bump_config_file}"

    if os.getenv("BUMP") is None:
        print(
            f"{print_prefix} just showing potential version paths, not incrementing version"
        )
        _cmd = f"bump-my-version show-bump {base_command}"
        subprocess.run(_cmd, shell=True)
        sys.exit(0)
    elif int(os.getenv("BUMP")) == 1:
        semver = "pre_n"
    else:
        semver = str(os.getenv("BUMP"))

    allowed_values = ["major", "minor", "patch", "pre_l", "pre_n"]

    if semver not in allowed_values:
        print(
            f"{print_prefix} error: allowed values for bump version are '{allowed_values}'"
        )
        sys.exit(1)

    print(f"{print_prefix} bumping to")

    _cmd = (
        "bump-my-version show "
        f"--increment --current-version {current_version} "
        f"{semver} new_version"
    )
    rec_output = subprocess.run(
        _cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        shell=True,
    )
    if rec_output.stdout != "":
        new_version = rec_output.stdout
    else:
        print(rec_output.stderr)
        sys.exit(1)
