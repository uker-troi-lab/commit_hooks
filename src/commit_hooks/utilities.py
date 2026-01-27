import os


def append_skip(string: str):
    # temporarily disable hooks: https://pre-commit.com/#temporarily-disabling-hooks
    cur_val = os.getenv("SKIP", "")
    if cur_val == "":
        return string
    else:
        return cur_val + "," + string
