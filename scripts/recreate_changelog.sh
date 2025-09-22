#!/bin/bash

# https://stackoverflow.com/a/28972460
if [ -a .commit ]
    then
    rm .commit
    cz -n cz_troi_hook ch --template scripts/CHANGELOG.md.j2
    git add CHANGELOG.md
    # --no-verify skips pre-commit and commit-msg hooks, but not
    # post-commit; this is why creating .commit file in commit-msg
    # hook is required and changelog is only created it this file exists
    git commit --amend --no-edit --no-verify
fi
exit
