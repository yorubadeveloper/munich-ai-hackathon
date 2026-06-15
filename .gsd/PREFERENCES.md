---
version: 1
mode: solo
custom_instructions:
  - Run pytest always like uv run pytest for the tests running
  - and also run uv run ruff for the linting
  - but this is only for the backend project
  - also we would need corresponding tests of the frontend and also linters from there
git:
  auto_push: false
  main_branch: main
  isolation: none
token_profile: burn-max
parallel:
  enabled: true
  merge_strategy: per-slice
  auto_merge: auto
  worker_model: proxy-local/claude-opus-4-7
slice_parallel:
  enabled: true
verification_commands:
  - pytest
---
# GSD Skill Preferences

See `~/.gsd/agent/extensions/gsd/docs/preferences-reference.md` for full field documentation and examples.
