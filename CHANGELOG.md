## Unreleased

### Bug Fixes

- another refactor to fix endless loop (bd29b78)
- env-var to skip bump-version (66f56e1)
- bump_version script (5628efa)
- cmd (02a43c8)
- commit args to cmd (f51e91b)
- bump cfg (a1215c8)
- bump cfg (e7fa87b)
- still fixiing endless loop (e211d9c)
- handling of residual files (5afe5e7)
- sys commands (a2d2241)
- exiting endless loop (9218e83)
- exiting endless loop (81c5e85)
- fixed issue with envar type (6c589f6)
- finalizing bump-version implementation (6003494)
- bump-show cmd (3e60e48)
- typo in bump-config (6a0f0a1)
- output of show-bump command (6cf32bc)
- fixed escape chars (d57ce8e)
- added bump-config as string into python script (5195bf1)
- missing closing quots (ce808c0)
- bump-my-version config to separate file (fcdcd9b)
- removed changing of directory (2f645cf)
- typo in hook-def and added exec-flag to script (2a9e567)
- fixed changelog-generation (1a49232)
- re-organized repo; customize template in class (31a1d4e)

### New Features

- added bump-version pre-push hook (30e2ae9)
- re-introduced the commit-args to bump-cfg (b305dc7)
- move bump-version hook to python (a877111)
- workaround to get correct version from project's pyproject.toml (7ee7e53)
- adding bump-version (wip) (0c95c69)
- make it os-iindependent by switching bash-scripts to python (55e002c)

### Other changes

- more logging (7cb685c)
- udpated errorhandling (cb35967)
- renamed temp-files for bump-version (eef7b22)
- introduce bump-version-helper (e6bc7cf)
- try fixing endless loops (531f685)
- also added skip-statement to changelog (104fb7f)
- **deps**: added missing tomli_w library (761dd43)
- last try for today (f669c26)
- trigger pipeline (75e424e)
- updated bump-script (0599931)
- try re-create changelog as pre-push stage (2d2d54a)
- try find out source of loop (3c1ab8a)
- another try, fixing duplicate execution (d2ea704)
- updated bump-version script (7539207)
- fixed print statement (0f39c0b)
- some more enhancements (f26171c)
- explicitly providing path to config file (f845095)
- echo config-file path (e063872)
- removed comments from .pre-commit-config (363e762)
- cleaning up repo (0ce7d4f)
- added comment (1624525)
- added comment (32813df)
- made scripts/recreate_changelog.sh executable (c398b7b)

### Refactor

- removed bash-script (cb16bf7)
