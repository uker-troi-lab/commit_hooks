#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

BUMPVERSION_CONFIG_FILE="$SCRIPT_DIR/bump_version.toml"

echo "[bump-version]: config file: $BUMPVERSION_CONFIG_FILE"

if ! command -v bump-my-version &> /dev/null; then
    echo "[bump-version]: error - bump-my-version is not installed. Please run `pip install bump-my-version`"
    exit 1
fi

# check if version is specified
if [ "$BUMP" == "" ]; then
    # quit silently, if bump is not set
    echo "[bump-version]: showing potential version paths, not incrementing version"

    exit 0
  elif [ "$BUMP" == "1" ]; then
    SEMVER="pre_n"
  else
    SEMVER=$BUMP
fi


if [ "$SEMVER" != "major" ] && [ "$SEMVER" != "minor" ] && [ "$SEMVER" != "patch" ] && [ "$SEMVER" != "pre_l" ] && [ "$SEMVER" != "pre_n" ] ; then
    usage
fi

PYTHON_EXEC="""
import tomllib
import os

with open("pyproject.toml", "rb") as f:
    toml_dict = tomllib.load(f)
print(toml_dict["project"]["version"])
"""

BUMPVERSION_CURRENT_VERSION=$(python -c $PYTHON_EXEC)

echo "[bump-version]: extracted version '$BUMPVERSION_CURRENT_VERSION' from pyproject.toml"

echo "[bump-version]: would bump version:"
NEWVER=$(bump-my-version show  \
  --config-file $BUMPVERSION_CONFIG_FILE \
  --increment --current-version $BUMPVERSION_CURRENT_VERSION \
  $SEMVER new_version
)
echo $NEWVER


# should commit be tagged? infer from version-bump
TAG_COMMIT="--no-tag"
if [[ "$NEWVER" ~= "dev" ]] ; then
    TAG_COMMIT="--tag"
fi

bump-my-version bump $TAG_COMMIT \
  --config-file $BUMPVERSION_CONFIG_FILE \
  --current-version $BUMPVERSION_CURRENT_VERSION \
  --new-version $NEWVER


PYTHON_TEMPDIR="import tempfile; print(tempfile.gettempdir())"

MSG_TMPDIR=$(python -c $PYTHON_TEMPDIR)

# save git message
# git log -1 --pretty=%B > /tmp/msg.txt
# only run commit-msg hook (to run changelog-helper)
# pre-commit run --hook-stage commit-msg --commit-msg-file /tmp/msg.txt
# run post-commit stage to generate changelog with new commit tag included
# pre-commit run --hook-stage post-commit
