# troi-lab commit hooks

This repo provides commit hooks for the troi-lab working group.


## Check Commit-Message

Check if commit message is valid with respect to conventional commits.

```yaml
- repo: https://github.com/uker-troi-lab/commit_hooks.git
  rev: main
  hooks:
    - id: check-commit-msg
```

## Changelog Helper

Need to specify both hooks to work.

```yaml
- repo: https://github.com/uker-troi-lab/commit_hooks.git
  rev: main
  hooks:
    - id: changelog-helper
    - id: recreate-changelog
```


## Version Bumper

Need to specify all three hooks to work.

```yaml
- repo: https://github.com/uker-troi-lab/commit_hooks.git
  rev: main
  hooks:
    - id: bump-version-helper
    - id: bump-version
    - id: bump-version-finalize
```

If you want to bump the version with one commit, prefix your commit command with `BUMP={val}`, where `val` can be one of `["major", "minor", "patch", "pre_l", "pre_n"]`.

`BUMP=1` is an alias for `BUMP=pre_n`.

When not specifying `BUMP`, the hook will show the potential bump-path. This can also be achivied running the following:

```bash
touch /tmp/.bump_version_temp_helper && pre-commit run --hook-stage post-commit bump-version
```

Hook `bump-version-finalize` is a pre-push hook that will push the tag, if HEAD was tagged.
