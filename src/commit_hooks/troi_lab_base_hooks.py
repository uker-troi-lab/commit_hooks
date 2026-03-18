#!/usr/bin/env python
import os
import sys
import subprocess


def troi_lab_base_hooks():
    config_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "templates",
        "configs",
    )
    cfg = os.path.join(config_path, "pre-commit-cfg.yaml")
    cmd = ["pre-commit", "run", "--config", cfg, "--files"] + sys.argv[1:]
    result = subprocess.run(cmd)
    sys.exit(result.returncode)
