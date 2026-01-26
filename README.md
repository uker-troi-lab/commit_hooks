# troi-lab commit hooks

This repo provides commit hooks for the troi-lab working group.


## Check Commit-Message [stage: commit-msg]

Check if commit message is valid with respect to [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).

```yaml
- repo: https://github.com/uker-troi-lab/commit_hooks.git
  rev: main
  hooks:
    - id: check-commit-msg
```

## Changelog Helper [stage: post-commit]

Generates a CHANGELOG.md from commit messages, that are formatted according to [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).

```yaml
- repo: https://github.com/uker-troi-lab/commit_hooks.git
  rev: main
  hooks:
    - id: recreate-changelog
```


## Version Bumper [stages: post-commit / pre-push]

Commit hook wrapper around [`bump-my-version`](https://github.com/callowayproject/bump-my-version).

```yaml
- repo: https://github.com/uker-troi-lab/commit_hooks.git
  rev: main
  hooks:
    - id: bump-version
    - id: bump-version-tag-pusher
```

If you want to bump the version with one commit, prefix your commit command with `BUMP={val}`, where `val` can be one of `["major", "minor", "patch", "pre_l", "pre_n"]`. `BUMP=1` is an alias for `BUMP=pre_n`.

When not specifying `BUMP`, the hook will show the potential bump-path. This can also be achivied running the following:

```bash
pre-commit run --hook-stage post-commit bump-version
```

To only trigger the version-bumping, you can run e.g.:

```bash
BUMP=patch pre-commit run --hook-stage post-commit bump-version
```

Hook `bump-version-tag-pusher` is a pre-push hook that will push the tag, if HEAD was tagged.
