#!/usr/bin/env python

import os
import sys
import tempfile
import subprocess

system_tempdir = tempfile.gettempdir()
temp_helper_file = os.path.join(system_tempdir, ".commit_temp_helper")


def changelog_helper():
    if not os.path.exists(temp_helper_file):
        # Create the file if it doesn't exist
        with open(temp_helper_file, "w"):
            pass
        # Set permissions to rw-r--r-- (0o644)
        os.chmod(temp_helper_file, 0o644)
    # always exit with status 0
    sys.exit(0)


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
    if os.path.exists(temp_helper_file):
        os.remove(temp_helper_file)
        os.environ["SKIP"] = "changelog-helper,recreate-changelog"
        _cmd = (
            "cz -n cz_troi_hook ch && "
            "git add CHANGELOG.md && "
            "git commit --no-verify --amend --no-edit"
        )
        subprocess.run(_cmd, shell=True)
    # always exit with status 0
    sys.exit(0)
