#!/usr/bin/env python
import sys
import subprocess
import argparse


def check_python_dependencies(rel_path: str = "./src"):
    print(f"Relative path: {rel_path}")
    cmd = ["check-dependencies", "--all", rel_path]
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def main(argv: str | None = None):
    _parser = argparse.ArgumentParser()
    _parser.add_argument("--rel_path", default="./src", type=str)
    args = _parser.parse_args(argv)
    check_python_dependencies(rel_path=args.rel_path)


if __name__ == "__main__":
    raise SystemExit(main())
