# Contributing

Thanks for helping improve AbletonBridge.

## Development Setup

```bash
uv sync --extra dev
```

## Checks

Run these before opening a pull request:

```bash
env -u PYTHONPATH uv run pytest -q
env -u PYTHONPATH uv run python -m compileall -q AbletonBridge_Remote_Script MCP_Server elevenlabs_mcp tests
git diff --check
```

`env -u PYTHONPATH` avoids importing packages from an embedding agent or shell environment instead of this project's virtual environment.

## Pull Requests

- Keep public changes generic and useful to all users.
- Do not commit personal project scripts, local generated files, `.env`, cache files, or compiled Python artifacts.
- Add or update tests for behavior changes.
- Prefer small focused pull requests.

## Optional Integrations

ElevenLabs and other provider credentials should be configured outside the repository. Use `.env.example` only as a placeholder reference.
