# Security Policy

## Supported versions

| Component | Status |
|-----------|--------|
| `main` branch | Supported |

Security fixes are applied to the `main` branch and released via the next deploy.

## Reporting a vulnerability

Please do **not** open a public issue for security problems. Instead, report privately by
opening a [security advisory](https://github.com/methila-2056/NaturaAI/security/advisories/new)
or emailing the maintainers directly.

Please include:

- The affected component (backend / frontend / ML engine) and endpoint or file
- A minimal reproduction, if possible
- The impact you observed

You should receive a response within 3 business days. We ask that you give us reasonable time to
fix and deploy the issue before disclosing it publicly.

## Security practices

- Secrets (`JWT_SECRET`, `DATABASE_URL`, `OPENAI_API_KEY`, OAuth credentials, SMTP passwords) live
  only in the hosting provider's dashboard (Render/Vercel/Neon). They are never committed.
- `.env` files are git-ignored; `.env.example` contains placeholders only.
- The backend uses JWT access tokens, stateless sessions, and scoped CORS origins
  (`ALLOWED_ORIGINS`). Endpoints that need auth are protected by `JwtAuthFilter`.
- The ML engine's `OPENAI_API_KEY` is server-side only; the frontend never receives it.
- Keep dependencies updated — Dependabot opens PRs weekly for Maven, npm, pip, and Actions.

## Data

User accounts are email + password (bcrypt) or Google OAuth. The app collects profile fields such
as age, gender, country, diseases, and allergies for personalization. Refer to the project's
privacy statement / terms for how this data is used.
