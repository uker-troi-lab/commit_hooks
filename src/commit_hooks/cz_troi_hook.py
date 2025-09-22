#!/usr/bin/env python

from commitizen.cz.conventional_commits import ConventionalCommitsCz
from jinja2 import PackageLoader


class TroiCommitizenCz(ConventionalCommitsCz):
    change_type_order = [
        "BREAKING CHANGE",
        "feat",
        "fix",
        "refactor",
        "revert",
        "perf",
        "docs",
        "test",
        "ci",
        "build",
        "style",
        "chore",
    ]
    # https://github.com/commitizen-tools/commitizen/blob/b76301d235b85610576dfd2c9f76933cb73183a1/commitizen/cz/conventional_commits/conventional_commits.py#L33
    # commit_parser = r"^((?P<change_type>feat|fix|refactor|perf|BREAKING CHANGE)(?:\((?P<scope>[^()\r\n]*)\)|\()?(?P<breaking>!)?|\w+!):\s(?P<message>.*)?"
    commit_parser = r"^((?P<change_type>build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(?:\((?P<scope>[^()\r\n]*)\)|\()?(?P<breaking>!)?|\w+!):\s(?P<message>.*)?"

    changelog_pattern = "^((BREAKING[\\-\\ ]CHANGE|\\w+)(\\(.+\\))?!?):"
    change_type_map = {
        "feat": "New Features",
        "fix": "Bug Fixes",
        "refactor": "Refactor",
        "perf": "Performance",
        "chore": "Other changes",
        "test": "Unit tests",
        "ci": "CI",
        "build": "Build",
        "docs": "Documentation",
        "style": "Style",
        "revert": "Revert",
    }

    template = "CHANGELOG.md.j2"
    template_loader = PackageLoader("commit_hooks", "templates")

    def schema_pattern(self) -> str:
        return r"^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test){1}(\([\w\-\.]+\))?(!)?: ([\w ])+([\s\S]*)"
