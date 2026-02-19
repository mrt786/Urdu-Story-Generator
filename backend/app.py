"""
Phase IV: FastAPI Microservice for Urdu Story Generation
Exposes the Trigram Language Model via a REST API.

Endpoints:
    GET  /health    - Health check
    POST /generate  - Generate an Urdu story (Input: prefix, max_length, temperature)
    GET  /model-info - Model statistics and metadata

Run:
    uvicorn app:app --host 0.0.0.0 --port 5000 --reload
"""

import os
import sys
import pickle
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

# ---------------------------------------------------------------------------
# Import model classes from Phase III
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'models'))
from trigram_model import StoryGeneratorAPI, TrigramLanguageModel

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PORT = 5000
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'trigram_model.pkl')

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Urdu Story Generator",
    description="Trigram Language Model microservice for generating Urdu stories",
    version="1.0.0",
)

# CORS – allow the React frontend (and any other origin) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Pydantic request / response schemas
# ---------------------------------------------------------------------------
class GenerateRequest(BaseModel):
    prefix: str = Field("", description="Starting phrase in Urdu")
    max_length: int = Field(500, ge=1, le=5000, description="Maximum tokens to generate")
    temperature: float = Field(0.8, ge=0.1, le=2.0, description="Sampling temperature")

class GenerateResponse(BaseModel):
    success: bool
    story: Optional[str] = None
    prefix: str
    error: Optional[str] = None

class ModelInfoResponse(BaseModel):
    model_type: str
    vocabulary_size: int
    total_tokens: int
    interpolation_weights: dict
    is_trained: bool

# ---------------------------------------------------------------------------
# Model loading helper (trains on the fly if .pkl is missing)
# ---------------------------------------------------------------------------

def ensure_model() -> StoryGeneratorAPI:
    """Load the pre-trained model or train one from preprocessed documents."""
    if os.path.exists(MODEL_PATH):
        return StoryGeneratorAPI(model_path=MODEL_PATH)

    print("Model not found — training from PreProcessing/Preprocessed_documents...")
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'PreProcessing', 'Preprocessed_documents')
    corpus = []
    if os.path.isdir(data_dir):
        for fname in sorted(os.listdir(data_dir)):
            if fname.endswith('.txt'):
                path = os.path.join(data_dir, fname)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        text = f.read().strip()
                        if text:
                            corpus.append(text)
                except Exception as e:
                    print(f"Warning: failed to read {path}: {e}")

    if not corpus:
        print("No preprocessed documents found — creating empty API instance.")
        return StoryGeneratorAPI(model_path=None)

    model = TrigramLanguageModel()
    model.train(corpus)

    model_data = {
        'lambda1': model.lambda1,
        'lambda2': model.lambda2,
        'lambda3': model.lambda3,
        'unigram_counts': dict(model.unigram_counts),
        'bigram_counts': {k: dict(v) for k, v in model.bigram_counts.items()},
        'trigram_counts': {k: dict(v) for k, v in model.trigram_counts.items()},
        'total_unigrams': model.total_unigrams,
        'bigram_context_counts': dict(model.bigram_context_counts),
        'trigram_context_counts': dict(model.trigram_context_counts),
        'vocabulary': model.vocabulary,
    }

    try:
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"Saved trained model to {MODEL_PATH}")
    except Exception as e:
        print(f"Warning: failed to save model: {e}")

    return StoryGeneratorAPI(model_path=MODEL_PATH)


# ---------------------------------------------------------------------------
# Load model at module level (works with both uvicorn and TestClient)
# ---------------------------------------------------------------------------
api_instance = ensure_model()
print("Model loaded — server is ready.")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    """Health-check endpoint."""
    return {"status": "ok", "message": "Backend is running"}


@app.get("/")
def root():
    """Root redirect to docs."""
    return {"status": "ok", "message": "Urdu Story Generator API — visit /docs for Swagger UI"}


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    """
    Generate an Urdu story from an optional prefix.

    - **prefix**: starting phrase in Urdu (empty string for no prompt)
    - **max_length**: maximum number of tokens to generate (1–5000)
    - **temperature**: sampling temperature; higher = more creative (0.1–2.0)
    """
    result = api_instance.generate(
        prefix=req.prefix,
        max_length=req.max_length,
        temperature=req.temperature,
    )
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Generation failed"))
    return GenerateResponse(
        success=True,
        story=result["story"],
        prefix=req.prefix,
    )


@app.get("/model-info", response_model=ModelInfoResponse)
def model_info():
    """Return model statistics and metadata."""
    model = api_instance.model
    return ModelInfoResponse(
        model_type="Trigram Language Model (MLE + Interpolation)",
        vocabulary_size=len(model.vocabulary),
        total_tokens=model.total_unigrams,
        interpolation_weights={
            "lambda1_unigram": model.lambda1,
            "lambda2_bigram": model.lambda2,
            "lambda3_trigram": model.lambda3,
        },
        is_trained=model.is_trained,
    )


# ---------------------------------------------------------------------------
# Entry-point for `python app.py`
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=PORT, reload=True)
