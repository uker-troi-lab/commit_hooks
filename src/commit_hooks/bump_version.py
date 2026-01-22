import subprocess
from sys import stdout
import os
import sys
import tempfile
import tomllib
import subprocess

print_prefix = "[bump-version]:"

system_tempdir = tempfile.gettempdir()
msg_helper_file = os.path.join(system_tempdir, ".commit_msg.txt")
bump_config_file = os.path.join(system_tempdir, ".bump_version.toml")
temp_helper_file = os.path.join(system_tempdir, ".versionbump_temp_helper")


def write_config(version, tag: bool = False):
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

    current_version = f'current_version = "{version}"'
    tag_handling = f"tag = {'true' if tag else 'false'}\n\n"

    cfg_file = bump_cfg_bumpversion + current_version + tag_handling + bump_cfg_parts
    print(cfg_file)

    print(f"{print_prefix} writing config file: {bump_config_file}")
    with open(bump_config_file, "w") as f:
        f.write(cfg_file)
    os.chmod(bump_config_file, 0o644)


def bump_version():
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

    write_config(version=current_version, tag=False)

    os.environ["BUMPVERSION_CURRENT_VERSION"] = current_version

    base_command = f"--config-file {bump_config_file}"

    if os.getenv("BUMP") is None:
        print(
            f"{print_prefix} just showing potential version paths, not incrementing version"
        )
        _cmd = f"bump-my-version show-bump {base_command}"
        subprocess.run(_cmd, shell=True)
        sys.exit(0)
    elif os.getenv("BUMP") == "1":
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

    tag_commit = False if "dev" in new_version else True
    write_config(version=current_version, tag=tag_commit)

    if not os.path.exists(temp_helper_file):
        # create helper file to avoid endless loops
        with open(temp_helper_file, "w"):
            pass
        # finally bump version
        _cmd = f"bump-my-version bump {base_command} --new-version {new_version}"
        subprocess.run(_cmd, shell=True)

        # recreate changelog if tag was generated
        if tag_commit:
            # save git message to temp folder
            subprocess.run(f"git log -1 --pretty=%B > {msg_helper_file}", shell=True)
            # only run commit-msg hook (to run changelog-helper)
            subprocess.run(
                f"pre-commit run --hook-stage commit-msg --commit-msg-file {msg_helper_file}",
                shell=True,
            )
            # run post-commit stage to generate changelog with new commit tag included
            subprocess.run("pre-commit run --hook-stage post-commit", shell=True)
    # remove temp files
    for f in [msg_helper_file, bump_config_file, temp_helper_file]:
        try:
            os.remove(f)
        except Exception:
            pass
    sys.exit(0)
