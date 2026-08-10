# Contributing to NaturaAI

Thanks for your interest in improving NaturaAI! This project is a final-year engineering
capstone: an AI-powered herbal remedy prediction and recommendation platform with a Spring Boot
backend, a Next.js frontend, and a FastAPI ML engine.

## Getting started

1. Fork the repository and clone it.
2. Follow the **Local Development** and **Environment Configuration** sections of the README.
3. Pick an issue (or open one) describing the change you want to make.
4. Branch from `main`: `git checkout -b feature/your-feature`.

## Project layout

```
backend/     Spring Boot 4 (Java 21) — REST API, JPA, JWT auth, heuristic fallback
frontend/    Next.js 15 (App Router) — React 19, Zustand, Tailwind, Vitest
ml-engine/   FastAPI — trained compatibility predictor + LLM assistant
docs/        Architecture and deployment notes
.github/     CI workflow and Dependabot config
```

## Code style & checks

Before pushing, make sure all checks pass — CI runs exactly these:

```bash
# Backend
cd backend && mvn -B verify

# Frontend
cd frontend && npm run lint && npm run test && npm run build

# ML engine
cd ml-engine && python -m pytest -q
```

- Follow the existing style (Lombok for the backend, `@/` path alias on the frontend, type hints
  in the ML engine). Do not add comments unless they explain non-obvious decisions.
- Keep secrets out of the repository — put new config behind `@Value`/env vars and document them
  in the relevant `.env.example`.

## Tests

- Backend: JUnit 5 + Mockito (`backend/src/test`). New service/controller logic should ship with
  tests.
- Frontend: Vitest + React Testing Library (`frontend/src/**/*.test.ts(x)`).
- ML engine: pytest (`ml-engine/tests`).

## Commits

Write clear, imperative commit messages (e.g. `Add pagination to herb search`). Reference the
issue number when applicable.

## Pull requests

- Open the PR against `main`.
- Summarise what changed and why, and mention how you verified it (tests run locally, etc.).
- Keep the diff focused; separate refactors from feature changes.
