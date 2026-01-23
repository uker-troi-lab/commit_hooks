import os
import sys


def generate_helper_file(fn: str):
    if not os.path.exists(fn):
        # Create the file if it doesn't exist
        with open(fn, "w"):
            pass
        # Set permissions to rw-r--r-- (0o644)
        os.chmod(fn, 0o644)
    # always exit with status 0
    sys.exit(0)
