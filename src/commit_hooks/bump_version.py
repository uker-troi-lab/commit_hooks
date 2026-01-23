import subprocess
from sys import stdout
import os
import sys
import tempfile
import tomllib
import subprocess
import re
import tomllib
import tomli_w

print_prefix = "[bump-version]:"

system_tempdir = tempfile.gettempdir()
msg_helper_file = os.path.join(system_tempdir, ".commit_msg.txt")
bump_config_file = os.path.join(system_tempdir, ".bump_version.toml")


def handle_config(version: str, pyproj_toml: dict | None = None):
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
    tag = false  # default this to false as we are tagging manually
    tag_name = "v{new_version}"
    tag_message = "release v{new_version}"
    allow_dirty = false
    message = "chore: bump version: {current_version} -> {new_version}"
    commit = false  # default this to false as we are committing manually
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

    add_cfg = f'current_version = "{version}"'

    cfg_file = bump_cfg_bumpversion + add_cfg + bump_cfg_parts

    # parse toml
    bump_toml_dict = tomllib.loads(cfg_file)
    # clean up the parse pattern
    bump_toml_dict["tool"]["bumpversion"]["parse"] = re.sub(
        r"\s+", "", bump_toml_dict["tool"]["bumpversion"]["parse"], flags=re.MULTILINE
    )

    if pyproj_toml is not None:
        # get tool entries, if defined
        tools = pyproj_toml.get("tool", {})
        if len(tools) > 0:
            # get bump-version entries, if defined
            custom_cfg = tools.get("bumpversion", {})
            if len(custom_cfg) > 1:
                # update default config
                for _k, _v in custom_cfg.items():
                    bump_toml_dict["tool"]["bumpversion"].update({_k: _v})
    # DEBUG
    # print(bump_toml_dict)
    # print(f"{print_prefix} writing config file: {bump_config_file}")

    # write config file
    with open(bump_config_file, "wb") as f:
        tomli_w.dump(bump_toml_dict, f)
    os.chmod(bump_config_file, 0o644)
    return bump_toml_dict


def bump_version():
    exit_code = 0
    # add env-var to skip bump-version pre-commit from now on
    os.environ["SKIP"] = "bump-version"
    try:
        # open pyproject toml from repo's root dir
        with open("pyproject.toml", "rb") as f:
            pyproj_toml_dict = tomllib.load(f)
        current_version = pyproj_toml_dict["project"]["version"]
        if len(current_version) == "":
            print(f"{print_prefix} failed to extract current version")
            sys.exit(1)
        else:
            print(
                f"{print_prefix} extracted current version '{current_version}' from pyproject.toml"
            )

        bump_toml_dict = handle_config(
            version=current_version, pyproj_toml=pyproj_toml_dict
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
            version_pattern = bump_toml_dict["tool"]["bumpversion"].get("parse", "")
            if version_pattern == "":
                print(
                    f"{print_prefix} ERROR: no version pattern (tool.bumpversion.parse) defined but required."
                )
                sys.exit(1)
            # remove unwanted characters from stdout output
            bump_pattern = re.compile(version_pattern)
            parse_version = bump_pattern.search(rec_output.stdout)
            try:
                new_version = parse_version.group()
            except Exception as e:
                print(e)
                sys.exit(1)

            print(f"{print_prefix} bumping to '{new_version}'")
        else:
            print(rec_output.stderr)
            sys.exit(1)

        tag_commit = False if "dev" in new_version else True

        # finally bump version
        _cmd = f"bump-my-version bump {base_command} --new-version {new_version}"
        subprocess.run(_cmd, shell=True)
        # update uv.lock with new version
        subprocess.run("uv lock", shell=True)
        commit_message = f"chore: bump version {current_version} -> {new_version}"
        _cmd = (
            "git add pyproject.toml uv.lock && "
            f'SKIP=bump-version git commit --no-verify -m "{commit_message}"'
        )
        subprocess.run(_cmd, shell=True)

        # save the changelog-msg
        subprocess.run(f"git log -1 --pretty=%B > {msg_helper_file}", shell=True)
        # only run commit-msg hook (to run changelog-helper)
        subprocess.run(
            f"pre-commit run --hook-stage commit-msg --commit-msg-file {msg_helper_file}",
            shell=True,
        )
        # run post-commit stage to generate changelog with new commit tag included
        subprocess.run(
            "SKIP=bump-version pre-commit run --hook-stage post-commit", shell=True
        )

        if tag_commit:
            # now, tag the release with the modified commit-sha
            subprocess.run(
                f'git tag -a v{new_version} -m "release v{new_version}"',
                shell=True,
            )
    except Exception as e:
        print(e)
        exit_code = 1

    # remove temp files
    for f in [msg_helper_file, bump_config_file]:
        try:
            os.remove(f)
        except Exception:
            pass
    sys.exit(exit_code)


if __name__ == "__main__":
    bump_version()
