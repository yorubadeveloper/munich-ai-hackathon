---
version: 1
mode: solo
custom_instructions:
  - Run pytest always like uv run pytest for the tests running
  - and also run uv run ruff for the linting
  - but this is only for the backend project
  - also we would need corresponding tests of the frontend and also linters from there
git:
  isolation: none
  main_branch: main
  auto_push: false
token_profile: burn-max
verification_commands:
  - pytest
---
# GSD Skill Preferences

See `~/.gsd/agent/extensions/gsd/docs/preferences-reference.md` for full field documentation and examples.
