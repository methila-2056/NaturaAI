# NaturaAI – Intelligent Herbal Remedy Prediction and Recommendation System

> **Disclaimer:** NaturaAI does not replace professional medical advice. Consult a qualified
> healthcare professional before consuming or applying any herbal remedy, especially if you have
> existing medical conditions, are pregnant, nursing, or taking prescription medications.

## Overview

NaturaAI is an AI-powered healthcare and herbal intelligence platform that helps users discover
safe and effective natural remedies using medicinal plants, herbs, flowers, roots, fruits, and
other naturally occurring ingredients.

The system acts as a combination of:

- Herbal Knowledge Base
- AI Recommendation Engine
- Medical Compatibility Predictor
- Natural Product Formulation Assistant
- Personalized Remedy Generator
- Large Language Model (LLM) Health Assistant

It determines whether two or more herbal ingredients can be safely combined, their benefits and
side effects, potential interactions, and produces personalized recommendations based on age,
gender, existing diseases, and internal/external treatment needs — along with preparation
methods, dosage, usage frequency, and a confidence score.

## Monorepo Layout

```
NaturaAI/
├── frontend/        # Next.js 15 (React, TypeScript, Tailwind, ShadCN-style UI, Framer Motion, Zustand)
├── backend/         # Spring Boot 4 / Java 21 (REST API, JWT + OAuth2, JPA, Redis, RabbitMQ)
├── ml-engine/       # Python (FastAPI, Scikit-Learn, XGBoost, LightGBM, TensorFlow, LangChain)
├── docs/            # Architecture + database schema documentation
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Tech Stack

| Layer     | Technology                                                        |
|-----------|-------------------------------------------------------------------|
| Frontend  | Next.js 15, React 19, TypeScript, Tailwind CSS 4, ShadCN UI, Framer Motion, Zustand |
| Backend   | Java 21, Spring Boot 4, Spring Security, Spring Data JPA, Hibernate, Maven, REST APIs |
| Database  | PostgreSQL (Supabase-compatible), pgAdmin 4                       |
| AI/ML     | Python, Scikit-Learn, TensorFlow, PyTorch, Hugging Face, LangChain |
| LLM       | Llama 4, Gemma, Mistral, OpenAI API (pluggable)                   |
| Vector DB | Qdrant                                                            |
| Auth      | JWT, OAuth2, Google Login                                         |
| Infra     | AWS S3, RabbitMQ, Redis, Docker, Docker Compose, GitHub Actions   |
| Deploy    | Vercel (frontend), Docker + Render (backend), Supabase PostgreSQL |

## Quick Start

### 1. Infrastructure (Docker)

```bash
docker compose up -d postgres redis rabbitmq qdrant
```

### 2. ML Engine

```bash
cd ml-engine
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Backend

```bash
cd backend
mvn spring-boot:run
```

Requires JDK 21 and Maven 3.9+. See `backend/README.md`.

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Environment Configuration

Copy `.env.example` to `.env` at the repository root and adjust values. Frontend and backend also
have their own `.env.example` files.

## Core Flow

1. Landing page (`/`)
2. Authentication — JWT + Google Sign-In (`/login`, `/register`)
3. User profile — age, gender, diseases, allergies, medications, lifestyle
4. Health information — diabetes, hypertension, asthma, PCOS, stress, etc.
5. Remedy type — internal (tea, juice, powder, capsules) or external (face wash, hair oil, soap)
6. Ingredient selection — upload image, text search, or pick from database
7. AI Prediction Engine — compatibility, safety/benefit/risk scores, toxicity, suitability,
   preparation, dosage, confidence
8. Dashboard — saved remedies, history, analytics, plant scanner

## Documentation

- [Architecture](docs/architecture.md)
- [Database Schema](docs/database-schema.md)

## License

Educational project for B.Tech CSE. Intended for informational purposes only.
