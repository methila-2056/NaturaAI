-- =====================================================================
-- NaturaAI - PostgreSQL 18 schema
-- The JPA layer (ddl-auto: update) is the source of truth at runtime;
-- this file documents the canonical schema and seeds the docker init.
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ------------------------- USERS & AUTH -----------------------------
CREATE TABLE IF NOT EXISTS users (
    id              BIGSERIAL PRIMARY KEY,
    email           VARCHAR(320) NOT NULL UNIQUE,
    password        VARCHAR(255) NOT NULL,
    full_name       VARCHAR(120) NOT NULL,
    role            VARCHAR(20)  NOT NULL DEFAULT 'USER',
    email_verified  BOOLEAN      NOT NULL DEFAULT FALSE,
    provider        VARCHAR(30),
    provider_id     VARCHAR(120),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS user_profiles (
    id                   BIGSERIAL PRIMARY KEY,
    user_id              BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    age                  INTEGER,
    gender               VARCHAR(30),
    height               DOUBLE PRECISION,
    weight               DOUBLE PRECISION,
    country              VARCHAR(100),
    lifestyle            VARCHAR(60),
    dietary_preferences  VARCHAR(120)
);

CREATE TABLE IF NOT EXISTS user_profile_diseases (
    user_profile_id BIGINT NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    diseases        VARCHAR(120) NOT NULL
);

CREATE TABLE IF NOT EXISTS user_profile_allergies (
    user_profile_id BIGINT NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    allergies       VARCHAR(120) NOT NULL
);

CREATE TABLE IF NOT EXISTS user_profile_medications (
    user_profile_id BIGINT NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    medications     VARCHAR(120) NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id           BIGSERIAL PRIMARY KEY,
    user_id      BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token        VARCHAR(512) NOT NULL UNIQUE,
    expires_at   TIMESTAMPTZ NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ------------------------- KNOWLEDGE BASE ---------------------------
CREATE TABLE IF NOT EXISTS herbs (
    id                  BIGSERIAL PRIMARY KEY,
    name                VARCHAR(120) NOT NULL UNIQUE,
    scientific_name     VARCHAR(200),
    family              VARCHAR(120),
    region              VARCHAR(200),
    active_compounds    VARCHAR(500),
    toxicity_level      VARCHAR(10) NOT NULL DEFAULT 'LOW'
);

CREATE TABLE IF NOT EXISTS herb_medicinal_properties (
    herb_id            BIGINT NOT NULL REFERENCES herbs(id) ON DELETE CASCADE,
    medicinal_properties VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS herb_benefits (
    herb_id   BIGINT NOT NULL REFERENCES herbs(id) ON DELETE CASCADE,
    benefits  VARCHAR(500) NOT NULL
);

CREATE TABLE IF NOT EXISTS herb_side_effects (
    herb_id      BIGINT NOT NULL REFERENCES herbs(id) ON DELETE CASCADE,
    side_effects VARCHAR(500) NOT NULL
);

CREATE TABLE IF NOT EXISTS herb_contraindications (
    herb_id          BIGINT NOT NULL REFERENCES herbs(id) ON DELETE CASCADE,
    contraindications VARCHAR(500) NOT NULL
);

CREATE TABLE IF NOT EXISTS herb_preparation_methods (
    herb_id             BIGINT NOT NULL REFERENCES herbs(id) ON DELETE CASCADE,
    preparation_methods VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS herb_combinations (
    id                    BIGSERIAL PRIMARY KEY,
    herb_a                VARCHAR(120) NOT NULL,
    herb_b                VARCHAR(120) NOT NULL,
    verdict               VARCHAR(20)  NOT NULL CHECK (verdict IN ('SAFE','CAUTION','UNSAFE')),
    compatibility_score   INTEGER NOT NULL CHECK (compatibility_score BETWEEN 0 AND 100),
    safety_score          INTEGER NOT NULL CHECK (safety_score BETWEEN 0 AND 100),
    benefit_score         INTEGER NOT NULL CHECK (benefit_score BETWEEN 0 AND 100),
    risk_score            INTEGER NOT NULL CHECK (risk_score BETWEEN 0 AND 100),
    scientific_confidence INTEGER NOT NULL CHECK (scientific_confidence BETWEEN 0 AND 100),
    toxicity_level        VARCHAR(10) NOT NULL DEFAULT 'LOW',
    UNIQUE (herb_a, herb_b)
);

CREATE TABLE IF NOT EXISTS herb_combination_benefits (
    combination_id BIGINT NOT NULL REFERENCES herb_combinations(id) ON DELETE CASCADE,
    benefits       VARCHAR(500) NOT NULL
);

CREATE TABLE IF NOT EXISTS herb_combination_risks (
    combination_id BIGINT NOT NULL REFERENCES herb_combinations(id) ON DELETE CASCADE,
    risks          VARCHAR(500) NOT NULL
);

CREATE TABLE IF NOT EXISTS diseases (
    id   BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS disease_symptoms (
    disease_id BIGINT NOT NULL REFERENCES diseases(id) ON DELETE CASCADE,
    symptoms   VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS disease_recommended_herbs (
    disease_id        BIGINT NOT NULL REFERENCES diseases(id) ON DELETE CASCADE,
    recommended_herbs VARCHAR(120) NOT NULL
);

CREATE TABLE IF NOT EXISTS disease_avoid_herbs (
    disease_id   BIGINT NOT NULL REFERENCES diseases(id) ON DELETE CASCADE,
    avoid_herbs  VARCHAR(120) NOT NULL
);

-- ------------------------- REMEDIES & RECOMMENDATIONS ---------------
CREATE TABLE IF NOT EXISTS remedies (
    id                  BIGSERIAL PRIMARY KEY,
    name                VARCHAR(200) NOT NULL,
    description         VARCHAR(1000),
    treatment_type      VARCHAR(20) NOT NULL CHECK (treatment_type IN ('INTERNAL','EXTERNAL')),
    recommended_quantity VARCHAR(120),
    usage_frequency     VARCHAR(120),
    created_by          BIGINT REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS remedy_ingredients (
    remedy_id   BIGINT NOT NULL REFERENCES remedies(id) ON DELETE CASCADE,
    ingredients VARCHAR(120) NOT NULL
);

CREATE TABLE IF NOT EXISTS remedy_preparation_steps (
    remedy_id         BIGINT NOT NULL REFERENCES remedies(id) ON DELETE CASCADE,
    preparation_steps VARCHAR(500) NOT NULL
);

CREATE TABLE IF NOT EXISTS recommendations (
    id                   BIGSERIAL PRIMARY KEY,
    user_id              BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    remedy_id            BIGINT REFERENCES remedies(id) ON DELETE SET NULL,
    ingredients          VARCHAR(2000) NOT NULL,
    treatment_type       VARCHAR(20) NOT NULL,
    verdict              VARCHAR(20) NOT NULL,
    compatibility_score  INTEGER,
    safety_score         INTEGER,
    benefit_score        INTEGER,
    risk_score           INTEGER,
    scientific_confidence INTEGER,
    rationale            VARCHAR(4000),
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ------------------------- SUPPORTING TABLES ------------------------
CREATE TABLE IF NOT EXISTS medical_references (
    id          BIGSERIAL PRIMARY KEY,
    title       VARCHAR(500) NOT NULL,
    source      VARCHAR(200),
    url         VARCHAR(1000),
    herb_id     BIGINT REFERENCES herbs(id) ON DELETE CASCADE,
    published_at DATE
);

CREATE TABLE IF NOT EXISTS images (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT REFERENCES users(id) ON DELETE CASCADE,
    s3_key      VARCHAR(500) NOT NULL,
    entity_type VARCHAR(60),
    entity_id   BIGINT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ai_logs (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT REFERENCES users(id) ON DELETE SET NULL,
    request    JSONB,
    response   JSONB,
    model_name VARCHAR(120),
    latency_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS user_history (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action     VARCHAR(60) NOT NULL,
    payload    JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_herb_combinations_pair
    ON herb_combinations (herb_a, herb_b);
CREATE INDEX IF NOT EXISTS idx_recommendations_user
    ON recommendations (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_user
    ON sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_ai_logs_created
    ON ai_logs (created_at DESC);
