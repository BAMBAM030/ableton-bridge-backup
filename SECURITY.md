# Security Policy

## Reporting a Vulnerability

Please do not open public issues for secrets, credential leaks, or vulnerabilities that could put users' Ableton projects or local machines at risk.

Use GitHub's private vulnerability reporting if it is available for this repository, or contact the maintainer through the repository owner profile.

## Secrets

Do not commit `.env` files or real API keys. Use `.env.example` for placeholders and configure real credentials through your MCP client environment, shell environment, or GitHub Actions secrets.

If a real secret is committed accidentally:

1. Revoke or rotate it at the provider immediately.
2. Remove it from the current tree.
3. Consider repository history cleanup if the value was exposed publicly.
