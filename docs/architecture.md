# NaturaAI Architecture

## System Overview

NaturaAI is a three-tier monorepo: a Next.js frontend, a Spring Boot REST API,
and a Python ML engine, plus PostgreSQL, Redis, RabbitMQ, and Qdrant for data,
cache, async messaging, and vector search.

```
Browser
  │
  ▼
┌──────────────┐      ┌───────────────────┐
│   Frontend   │      │      Backend      │
│  Next.js 15  │─────▶│  Spring Boot 4    │────▶ PostgreSQL 18
│ React/Tailwind│ HTTP │  JWT + OAuth2     │───▶ Redis (cache)
└──────────────┘      │  JPA / Hibernate   │───▶ RabbitMQ (async)
                      └────────┬──────────┘
                               │ REST
                      ┌────────▼──────────┐
                      │    ML Engine      │───▶ Qdrant (vectors)
                      │   FastAPI (Py)    │───▶ models/*.joblib
                      └────────┬──────────┘
                               │ optional
                               ▼
                       LLM (Llama 4 / Gemma / Mistral / OpenAI)
```

## AI Architecture Layers

1. **Knowledge Base** — curated herbal datasets (plants, combinations,
   diseases) in PostgreSQL (backend) and CSV (ML engine).
2. **Vector Database** — Qdrant stores embeddings of herb descriptions and
   research snippets for semantic retrieval.
3. **Embedding Model** — Hugging Face sentence transformers embed herb
   properties and user queries (pluggable; stubbed in the scaffold).
4. **ML Prediction** — ensemble of Random Forest / XGBoost / Gradient
   Boosting / LightGBM trained on pair records. `train/train_predictor.py`
   produces `models/predictor.joblib`.
5. **LLM** — retrieval-first assistant (`ml-engine/app/assistant.py`) answers
   from the knowledge base, with optional LLM-backed explanation.
6. **Recommendation Engine** — combines profile (age, gender, diseases,
   allergies, medications) with disease-to-herb mapping to score candidates.
7. **Frontend Dashboard** — renders scores, benefits, risks, preparation
   steps, and safety warnings.

## Request Flow — Remedy Analysis

1. User selects ingredients + remedy type on `/analyze`.
2. Frontend POSTs to `POST /api/v1/remedies/analyze` (backend).
3. Backend forwards to ML engine `POST /predict` via `MlEngineClient`.
4. If the ML engine is unavailable, `AnalysisService` falls back to the
   rule-based engine (curated pair lookup + contraindication rules).
5. Result (scores, verdict, benefits, risks, preparation, dosage) is returned
   to the frontend and rendered as cards. Optionally persisted as a
   `Recommendation`.

## Authentication

- Email/password → BCrypt hash stored in `users`; successful login issues a
  stateless JWT (jjwt) signed with a 32+ byte secret.
- `JwtAuthFilter` validates `Authorization: Bearer <token>` on every request.
- Google Sign-In via Spring Security OAuth2 client; the `OAuth2SuccessHandler`
  exchanges the OAuth2 user for a NaturaAI JWT and redirects to
  `<frontend-url>/login?token=...`.
- Redis caches herb lookups (`@Cacheable("herbs")`) and can back sessions.

## Async & Infra

- RabbitMQ is wired for audit/notification jobs (e.g. AI log ingestion);
  endpoints are scaffolded in `application.yml`.
- Docker Compose runs postgres, pgadmin, redis, rabbitmq, qdrant, ml-engine,
  backend, frontend.

## Environment

See root `.env.example`. Per-service defaults keep local development running
with `docker compose up -d postgres redis rabbitmq qdrant` + local
`mvn` / `uvicorn` / `npm run dev`.

## Deployment Targets

- Frontend → Vercel (env: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_ML_URL`)
- Backend → Docker + Render (`SPRING_PROFILES_ACTIVE=docker`)
- Database → Supabase PostgreSQL (set `DB_HOST` etc.)
- Storage → AWS S3 (images, scanned plants)
- CI/CD → GitHub Actions (`.github/workflows/ci.yml`) builds all three tiers
