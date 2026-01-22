#!/usr/bin/env bash

set -e

# change to project root
cd "$(dirname "$(dirname "$0")")"

if ! command -v bump-my-version &> /dev/null; then
    echo "[bump-version]: error - bump-my-version is not installed. Please run `pip install bump-my-version`"
    exit 1
fi

# check if version is specified
if [ "$BUMP" == "" ]; then
    # quit silently, if bump is not set
    echo "[bump-version]: showing potential version paths, not incrementing version"
    bump-my-version show-bump
    exit 0
  elif [ "$BUMP" == "1" ]; then
    SEMVER="pre_n"
  else
    SEMVER=$BUMP
fi


if [ "$SEMVER" != "major" ] && [ "$SEMVER" != "minor" ] && [ "$SEMVER" != "patch" ] && [ "$SEMVER" != "pre_l" ] && [ "$SEMVER" != "pre_n" ] ; then
    usage
fi


echo "[bump-version]: would bump version:"
NEWVER=$(bump-my-version show --increment $SEMVER new_version)
echo $NEWVER


# should commit be tagged? infer from version-bump
TAG_COMMIT="--no-tag"
if [[ $NEWVER != "dev" ]] ; then
    TAG_COMMIT="--tag"
fi

bump-my-version $TAG_COMMIT $NEWVER

# save git message
# git log -1 --pretty=%B > /tmp/msg.txt
# only run commit-msg hook (to run changelog-helper)
# pre-commit run --hook-stage commit-msg --commit-msg-file /tmp/msg.txt
# run post-commit stage to generate changelog with new commit tag included
# pre-commit run --hook-stage post-commit
