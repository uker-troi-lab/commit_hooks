#!/usr/bin/env python

# import os
import sys
import tempfile
import subprocess
from .utilities import generate_helper_file, append_skip

system_tempdir = tempfile.gettempdir()
# temp_helper_file = os.path.join(system_tempdir, ".commit_temp_helper")


def changelog_helper():
    # generate_helper_file(fn=temp_helper_file)
    generate_helper_file()


# original bash-script (which worked well)
# https://stackoverflow.com/a/28972460
# if [ -a .commit ]
#     then
#     rm .commit
#     cz -n cz_troi_hook ch
#     git add CHANGELOG.md
#     # --no-verify skips pre-commit and commit-msg hooks, but not
#     # post-commit; this is why creating .commit file in commit-msg
#     # hook is required and changelog is only created it this file exists
#     git commit --amend --no-edit --no-verify
# fi
# exit


def recreate_changelog():
    # if os.path.exists(temp_helper_file):
    skip_string = (
        "check-commit-msg,"
        "changelog-helper,"
        "recreate-changelog,"
        "bump-version-helper,"
        "bump-version,"
        "bump-version-tag-pusher"
    )
    skip_var = append_skip(skip_string)
    _cmd = (
        "cz -n cz_troi_hook ch && "
        "git add CHANGELOG.md && "
        f"SKIP={skip_var} git commit --no-verify --amend --no-edit"
    )
    subprocess.run(_cmd, shell=True)
    # os.remove(temp_helper_file)
    # always exit with status 0
    sys.exit(0)
