"""NaturaAI ML Engine - FastAPI application.

Endpoints:
- POST /predict        remedy compatibility prediction (matches backend DTO)
- POST /recommend      personalized recommendation
- POST /suggest        AI-ranked complementary ingredient suggestions
- POST /assistant      grounded herbal Q&A
- POST /recognize      plant identification from an uploaded image
- GET  /herbs          list known herbs
- GET  /health         liveness check
"""

from __future__ import annotations

import io

import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from . import knowledge
from .assistant import answer
from .plant_recognition import recognize_pixels
from .predictor import CompatibilityPredictor
from .recommender import RecommendationEngine

app = FastAPI(
    title="NaturaAI ML Engine",
    description="Herbal compatibility prediction, personalized recommendations, and grounded Q&A.",
    version="0.1.0",
)

predictor = CompatibilityPredictor()
recommender = RecommendationEngine(predictor)


class Profile(BaseModel):
    age: int | None = None
    gender: str | None = None
    diseases: list[str] = []
    allergies: list[str] | None = None
    medications: list[str] | None = None


class PredictRequest(BaseModel):
    ingredients: list[str]
    remedyType: str = "internal"
    profile: Profile | None = None


class RecommendRequest(BaseModel):
    diseases: list[str]
    treatmentType: str = "internal"
    allergies: list[str] = []
    age: int | None = None
    gender: str | None = None
    limit: int = 3


class AssistantRequest(BaseModel):
    query: str


class SuggestRequest(BaseModel):
    ingredient: str
    limit: int = 5
    exclude: list[str] = []
    remedyType: str = "internal"


@app.get("/health")
def health() -> dict:
    return {"status": "UP", "service": "naturaai-ml-engine"}


@app.get("/herbs")
def herbs() -> list[dict]:
    return knowledge.load_plants()


@app.post("/predict")
def predict(request: PredictRequest) -> dict:
    if len(request.ingredients) < 2:
        raise HTTPException(status_code=422, detail="At least two ingredients are required.")
    return predictor.predict(request.ingredients, request.remedyType)


@app.post("/recommend")
def recommend(request: RecommendRequest) -> dict:
    suggestions = recommender.recommend(
        diseases=request.diseases,
        treatment_type=request.treatmentType,
        allergies=request.allergies,
        age=request.age,
        gender=request.gender,
        limit=request.limit,
    )
    return {"recommendations": suggestions}


@app.post("/assistant")
def assistant(request: AssistantRequest) -> dict:
    return answer(request.query)


@app.post("/suggest")
def suggest(request: SuggestRequest) -> dict:
    if knowledge.find_plant(request.ingredient) is None:
        raise HTTPException(status_code=422, detail=f"Unknown ingredient: {request.ingredient}")
    suggestions = predictor.suggest_complements(
        ingredient=request.ingredient,
        limit=request.limit,
        exclude=request.exclude,
        remedy_type=request.remedyType,
    )
    return {"ingredient": request.ingredient, "suggestions": suggestions}


@app.post("/recognize")
async def recognize(file: UploadFile = File(...)) -> dict:
    try:
        from PIL import Image

        data = await file.read()
        image = Image.open(io.BytesIO(data))
        pixels = np.asarray(image.convert("RGB"))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not decode the uploaded image.")

    result = recognize_pixels(pixels)
    result["filename"] = file.filename
    return result
