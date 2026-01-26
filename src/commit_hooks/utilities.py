import os
import sys


def generate_helper_file(fn: str | None = None):
    # if not os.path.exists(fn):
    #     # Create the file if it doesn't exist
    #     with open(fn, "w"):
    #         pass
    #     # Set permissions to rw-r--r-- (0o644)
    #     os.chmod(fn, 0o644)
    print(
        "Creating helper-file is deprecated. This hook will be removed in a future release."
    )
    # always exit with status 0
    sys.exit(0)


def append_skip(string: str):
    cur_val = os.getenv("SKIP", "")
    if cur_val == "":
        return string
    else:
        return cur_val + "," + string
