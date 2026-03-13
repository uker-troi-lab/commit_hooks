#!/usr/bin/env python
import os
import sys

HERE = os.path.dirname(os.path.realpath(__file__))


def troi_lab_base_hooks():
    cfg = os.path.join(HERE, ".pre-commit-config.yaml")
    cmd = ['pre-commit', 'run', '--config', cfg, '--files'] + sys.argv[1:]
    os.execvp(cmd[0], cmd)
    sys.exit(0)


# if __name__ == '__main__':
#     exit(main())
