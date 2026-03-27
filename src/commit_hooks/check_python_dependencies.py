#!/usr/bin/env python
import sys
import subprocess


def check_python_dependencies():
    cmd = ["check-dependencies", "--all", "./src"]
    result = subprocess.run(cmd)
    sys.exit(result.returncode)
