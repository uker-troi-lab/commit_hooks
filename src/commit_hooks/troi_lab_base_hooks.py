#!/usr/bin/env python
import os
import sys


def troi_lab_base_hooks():
    root_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates","configs")
    cfg = os.path.join(root_path, ".pre-commit-config.yaml")
    cmd = ["pre-commit", "run", "--config", cfg, "--files"] + sys.argv[1:]
    os.execvp(cmd[0], cmd)
    sys.exit(0)
