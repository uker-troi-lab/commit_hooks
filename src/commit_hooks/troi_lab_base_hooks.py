#!/usr/bin/env python
import os
import sys
import subprocess


def troi_lab_base_hooks(yaml_file: str = "pre-commit-cfg_base.yaml"):
    config_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "templates",
        "configs",
    )
    cfg = os.path.join(config_path, yaml_file)
    cmd = ["pre-commit", "run", "--config", cfg, "--files"] + sys.argv[1:]
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def troi_lab_base_hooks_python():
    troi_lab_base_hooks(yaml_file="pre-commit-cfg_python.yaml")
