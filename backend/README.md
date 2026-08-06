# NaturaAI Backend

Spring Boot 4 / Java 21 REST API for NaturaAI.

## Prerequisites

- JDK 21
- Maven 3.9+
- PostgreSQL 18 (or `docker compose up -d postgres` from the repo root)
- Optional: Redis, RabbitMQ, Qdrant, ML engine

## Run locally

```bash
docker compose up -d postgres redis rabbitmq qdrant
mvn spring-boot:run
```

The API runs at http://localhost:8080. OpenAPI/health endpoints:
- `GET /api/v1/health`
- `GET /actuator/health`

## Run with Docker

```bash
docker compose build backend
docker compose up backend
```

## Endpoints

| Method | Path                    | Description                          | Auth |
|--------|-------------------------|--------------------------------------|------|
| POST   | /api/v1/auth/register   | Create account + JWT                 | No   |
| POST   | /api/v1/auth/login      | Login with email/password + JWT      | No   |
| GET    | /api/v1/users/me        | Current user profile                 | Yes  |
| PUT    | /api/v1/users/me        | Update profile (diseases, allergies) | Yes  |
| GET    | /api/v1/herbs           | All herbs                            | No   |
| GET    | /api/v1/herbs/search?q= | Search herbs                         | No   |
| POST   | /api/v1/remedies/analyze| AI remedy analysis                   | No   |

## Configuration

Environment variables (see root `.env.example`):

- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `JWT_SECRET`, `JWT_EXPIRATION_MS`
- `ML_ENGINE_URL` (default `http://localhost:8000`)
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- `REDIS_HOST`, `RABBIT_HOST`

## Notes

- The analysis endpoint calls the Python ML engine; if it is unreachable it falls back to the
  built-in rule-based `AnalysisService`.
- `DataSeeder` populates a starter set of herbs, combinations, and diseases on first boot.
- JWT secret must be at least 32 bytes in production.
