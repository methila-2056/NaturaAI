# NaturaAI ML Engine

Python service powering the AI features: compatibility prediction, personalized
recommendations, plant recognition, and the grounded herbal assistant.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Interactive docs: http://localhost:8000/docs

## Endpoints

| Method | Path          | Description                                       |
|--------|---------------|---------------------------------------------------|
| GET    | /health       | Liveness check                                    |
| GET    | /herbs        | List herbs from the knowledge base                |
| POST   | /predict      | Compatibility prediction (matches backend DTO)    |
| POST   | /recommend    | Personalized recommendation                       |
| POST   | /assistant    | Grounded herbal Q&A                               |
| POST   | /recognize    | Plant identification from uploaded image          |

## Data

Starter CSV datasets in `data/`:

- `plants.csv` — plant properties, benefits, side effects, toxicity
- `combinations.csv` — curated pair verdicts and scores
- `diseases.csv` — disease-to-herb recommendation/avoidance mapping

## Training the ML model

```bash
python -m train.train_predictor
```

Trains Random Forest, Gradient Boosting, XGBoost, and LightGBM on the
combination records and saves the best to `models/predictor.joblib`, which the
predictor loads automatically at startup.

## LLM integration

The assistant answers from the knowledge base first. Set `OPENAI_API_KEY` to
enable live LLM responses, or point `OPENAI_BASE_URL` at a local Llama 4 /
Gemma / Mistral server (Ollama, vLLM) with `LLM_MODEL` set.

## Plant recognition

`app/plant_recognition.py` is a placeholder that swaps in a trained
EfficientNet / ResNet50 / Vision Transformer checkpoint. Enable the TensorFlow
or PyTorch extras in `requirements.txt` to train the real model.
