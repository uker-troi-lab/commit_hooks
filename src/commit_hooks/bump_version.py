import subprocess
from sys import stdout
import os
import sys
import tempfile
import tomllib
import subprocess

bump_cfg_bumpversion = '''
[tool.bumpversion]
parse = """
  (?P<major>0|[1-9]\\\\d*)\\\\.
  (?P<minor>0|[1-9]\\\\d*)\\\\.
  (?P<patch>0|[1-9]\\\\d*)
  (?:
      -
      (?P<pre_l>[a-zA-Z-]+)
      (?P<pre_n>0|[1-9]\\\\d*)
  )?
"""
serialize = [
    "{major}.{minor}.{patch}-{pre_l}{pre_n}",
    "{major}.{minor}.{patch}",
]
search = "{current_version}"
replace = "{new_version}"
regex = false
ignore_missing_version = false
sign_tags = false
tag_name = "v{new_version}"
tag_message = "release v{new_version}"
allow_dirty = false
commit = true
message = "chore: bump version: {current_version} -> {new_version}"
commit_args = "--no-verify"
'''

bump_cfg_parts = """
[tool.bumpversion.parts.pre_l]
values = ["dev", "rc", "final"]
optional_value = "final"

[[tool.bumpversion.files]]
filename = "pyproject.toml"
search = "version = \\"{current_version}\\""
replace = "version = \\"{new_version}\\""

"""

print_prefix = "[bump-version]:"

system_tempdir = tempfile.gettempdir()
msg_helper_file = os.path.join(system_tempdir, ".commit_msg.txt")
bump_config_file = os.path.join(system_tempdir, ".bump_version.toml")
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

with open(bump_config_file, "w") as f:
    f.write(
        bump_cfg_bumpversion
        + f'current_version = "{current_version}"\n\n'
        + bump_cfg_parts
    )
os.chmod(bump_config_file, 0o644)


def bump_version():
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

    _cmd = f"bump-my-version show {base_command} --increment {semver} new_version"
    rec_output = subprocess.run(
        _cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        shell=True,
    )
    if rec_output.stdout != "":
        new_version = rec_output.stdout
        print(f"{print_prefix} bumping to '{new_version}'")
    else:
        print(rec_output.stderr)
        sys.exit(1)
