import subprocess
import os
import sys
import tempfile
import tomllib
import re
import tomli_w
from .utilities import generate_helper_file, append_skip

print_prefix = "[bump-version]:"

system_tempdir = tempfile.gettempdir()
msg_helper_file = os.path.join(system_tempdir, ".bump_version_commit_msg.txt")
bump_config_file = os.path.join(system_tempdir, ".bump_version.toml")
# temp_helper_file = os.path.join(system_tempdir, ".bump_version_temp_helper")


def bump_version_helper():
    # generate_helper_file(fn=temp_helper_file)
    generate_helper_file()


def get_bumpversion_cfg():
    bump_cfg_bumpversion = '''
    [tool.bumpversion]
    parse = """
      (?P<major>0|[1-9]\\\\d*)\\\\.
      (?P<minor>0|[1-9]\\\\d*)\\\\.
      (?P<patch>0|[1-9]\\\\d*)
      (?:
          (?P<pre_l>[a-zA-Z-]+)
          (?P<pre_n>0|[1-9]\\\\d*)
      )?
    """
    serialize = [
        "{major}.{minor}.{patch}{pre_l}{pre_n}",
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
    '''

    bump_cfg_parts = """
    [tool.bumpversion.parts.pre_l]
    values = ["dev"]

    [[tool.bumpversion.files]]
    filename = "pyproject.toml"
    search = "version = \\"{current_version}\\""
    replace = "version = \\"{new_version}\\""
    """

    cfg_file = bump_cfg_bumpversion + bump_cfg_parts

    # parse toml
    bump_toml_dict = tomllib.loads(cfg_file)
    # clean up the parse pattern
    bump_toml_dict["tool"]["bumpversion"]["parse"] = re.sub(
        r"\s+", "", bump_toml_dict["tool"]["bumpversion"]["parse"], flags=re.MULTILINE
    )

    return bump_toml_dict


def handle_config(version: str, pyproj_toml: dict | None = None):
    bump_toml_dict = get_bumpversion_cfg()
    # update version
    bump_toml_dict["tool"]["bumpversion"]["current_version"] = version

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

    # always default:
    bump_toml_dict["tool"]["bumpversion"].update(
        {
            "commit": False,  # default this to false as we are committing manually
            "tag": False,
        }
    )

    # write config file
    with open(bump_config_file, "wb") as f:
        tomli_w.dump(bump_toml_dict, f)
    os.chmod(bump_config_file, 0o644)
    return bump_toml_dict


def validate_version(validate_string: str, bump_toml_dict: dict):
    exit_code = None
    version_pattern = bump_toml_dict["tool"]["bumpversion"].get("parse", "")
    if version_pattern == "":
        print(
            f"{print_prefix} ERROR: no version pattern (tool.bumpversion.parse) defined but required."
        )
        exit_code = 1
    # remove unwanted characters from stdout output
    bump_pattern = re.compile(version_pattern)
    parse_version = bump_pattern.search(validate_string)
    try:
        if parse_version is not None:
            new_version = parse_version.group()
    except Exception as e:
        new_version = ""
        exit_code = 1
        print(e)

    return new_version, exit_code


def bump_version():
    exit_code = None
    try:
        # if os.path.exists(temp_helper_file):
        # open pyproject toml from repo's root dir
        with open("pyproject.toml", "rb") as f:
            pyproj_toml_dict = tomllib.load(f)
        current_version = pyproj_toml_dict["project"]["version"]
        if len(current_version) == "":
            exit_code = 1
            raise Exception(f"{print_prefix} failed to extract current version")
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
            _cmd = f"bump-my-version show-bump {base_command}"
            subprocess.run(_cmd, shell=True)
            exit_code = 0
            raise Exception(
                f"{print_prefix} just showing potential version paths, not incrementing version"
            )
        elif os.getenv("BUMP") == "1":
            semver = "pre_n"
        else:
            semver = str(os.getenv("BUMP"))

        allowed_values = ["major", "minor", "patch", "pre_l", "pre_n"]

        if semver not in allowed_values:
            exit_code = 1
            raise Exception(
                f"{print_prefix} error: allowed values for bump version are '{allowed_values}'"
            )

        _cmd = f"bump-my-version show {base_command} --increment {semver} new_version"
        rec_output = subprocess.run(
            _cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            shell=True,
        )
        if rec_output.stdout != "":
            new_version, new_exit_code = validate_version(
                validate_string=rec_output.stdout, bump_toml_dict=bump_toml_dict
            )
            if new_exit_code is not None:
                exit_code = new_exit_code
            print(f"{print_prefix} bumping to '{new_version}'")
        else:
            print(rec_output.stderr)
            exit_code = 1

        if exit_code == 1:
            raise Exception(f"{print_prefix} ERROR")

        tag_commit = False if "dev" in new_version else True

        # finally bump version
        _cmd = f"bump-my-version bump {base_command} --new-version {new_version}"
        subprocess.run(_cmd, shell=True)
        # update uv.lock with new version
        subprocess.run("uv lock", shell=True)

        # compose skip string
        skip_string = "bump-version-helper,bump-version,bump-version-tag-pusher"
        skip_var = append_skip(skip_string)

        # compose commit message
        commit_message = eval(
            'f"' + bump_toml_dict["tool"]["bumpversion"]["message"] + '"'
        )
        _cmd = (
            "git add pyproject.toml uv.lock && "
            f'SKIP={skip_var} git commit --no-verify -m "{commit_message}"'
        )
        subprocess.run(_cmd, shell=True)

        # save the changelog-msg
        subprocess.run(f"git log -1 --pretty=%B > {msg_helper_file}", shell=True)

        # compose skip string
        skip_string = (
            "changelog-helper,"
            "recreate-changelog,"
            "bump-version-helper,"
            "bump-version,"
            "bump-version-tag-pusher"
        )
        skip_var = append_skip(skip_string)
        # only run commit-msg hook (to run changelog-helper)
        subprocess.run(
            f"SKIP={skip_var} pre-commit run --hook-stage commit-msg --commit-msg-file {msg_helper_file}",
            shell=True,
        )

        # compose skip string
        skip_string = "bump-version-helper,bump-version,bump-version-tag-pusher"
        skip_var = append_skip(skip_string)
        # run post-commit stage to generate changelog with new commit tag included
        subprocess.run(
            f"SKIP={skip_var} pre-commit run --hook-stage post-commit", shell=True
        )

        if tag_commit:
            tag_name = eval(
                'f"' + bump_toml_dict["tool"]["bumpversion"]["tag_name"] + '"'
            )
            tag_message = eval(
                'f"' + bump_toml_dict["tool"]["bumpversion"]["tag_message"] + '"'
            )
            # now, tag the release with the modified commit-sha
            subprocess.run(
                f'git tag -a {tag_name} -m "{tag_message}"',
                shell=True,
            )
    except Exception as e:
        print(e)
        if exit_code is None:
            exit_code = 1

    # default value, if exit_code hasn't set so far
    if exit_code is None:
        exit_code = 0
    # remove temp files
    # for f in [msg_helper_file, bump_config_file, temp_helper_file]:
    for f in [msg_helper_file, bump_config_file]:
        try:
            os.remove(f)
        except Exception:
            pass
    sys.exit(exit_code)


def bump_version_tagpusher():
    bump_toml_dict = get_bumpversion_cfg()

    _cmd = "git describe --exact-match --tags HEAD"
    rec_output = subprocess.run(
        _cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        shell=True,
    )
    new_version, new_exit_code = validate_version(
        validate_string=rec_output.stdout, bump_toml_dict=bump_toml_dict
    )
    if new_exit_code is None and new_version != "":
        # https://github.com/pre-commit/pre-commit.com/blob/main/sections/advanced.md#pre-push
        remote_name = os.getenv("PRE_COMMIT_REMOTE_NAME", "origin")
        tag_name = eval('f"' + bump_toml_dict["tool"]["bumpversion"]["tag_name"] + '"')
        # if we got a valid tag, we can push it
        commit_sha = os.getenv("PRE_COMMIT_TO_REF", "")
        print(f"{print_prefix} tagging commit '{commit_sha}' as {tag_name}")
        _cmd = (
            f"SIP=bump-version-tag-pusher git push --no-verify {remote_name} {tag_name}"
        )
        subprocess.run(_cmd, shell=True)
    # always exit with status 0
    # try:
    #     os.remove(temp_helper_file)
    # except Exception:
    #     pass
    sys.exit(0)
