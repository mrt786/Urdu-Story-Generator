# ============================================
# Dockerfile – Urdu Story Generator Microservice
# ============================================
FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr (useful for Docker logs)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ── Install Python dependencies ───────────────────────
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application code & data ──────────────────────
COPY models/                        ./models/
COPY backend/                       ./backend/
COPY Tokenization/                  ./Tokenization/
COPY PreProcessing/Preprocessed_documents/ ./PreProcessing/Preprocessed_documents/

# ── Expose the API port ──────────────────────────────
EXPOSE 5000

# ── Run FastAPI via uvicorn ──────────────────────────
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "5000"]
