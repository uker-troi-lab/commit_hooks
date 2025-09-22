#!/usr/bin/env python

from commitizen.cz.conventional_commits import ConventionalCommitsCz


class HooksCommitizenCz(ConventionalCommitsCz):
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
    commit_parser = r"^(?P<change_type>build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test){1}(\((?P<scope>[\w\-\.]+)\))?(?P<breaking>!)?:\s(?P<message>.*)?"

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

    def schema_pattern(self) -> str:
        return r"^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test){1}(\([\w\-\.]+\))?(!)?: ([\w ])+([\s\S]*)"
