# Backend - Urdu Story Generator API

Simple Flask API for the Urdu Story Generator using a Trigram Language Model.

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Ensure Model File Exists

The model expects a trained model file at: `../models/trigram_model.pkl`

If this file doesn't exist, you'll need to train the model first using the preprocessing and model training scripts.

### 3. Run the Backend

```bash
python app.py
```

The backend will start at `http://localhost:5000`

## API Endpoints

### 1. Health Check
```
GET /health
```
Response:
```json
{
  "status": "ok",
  "message": "Backend is running"
}
```

### 2. Generate Story
```
POST /generate
Content-Type: application/json

{
  "prefix": "ایک دن",
  "max_length": 500,
  "temperature": 0.8
}
```

Response:
```json
{
  "success": true,
  "story": "ایک دن...",
  "prefix": "ایک دن"
}
```

### 3. Generate Story (Simple GET)
```
GET /generate?prefix=ایک دن&max_length=500&temperature=0.8
```

## Parameters

- **prefix** (string): Starting text for story generation (optional)
- **max_length** (integer): Maximum length of generated text (default: 500)
- **temperature** (float): Controls randomness/creativity (default: 0.8)
  - Lower values (0.1-0.5) = more consistent
  - Higher values (1.0+) = more random/creative

## Requirements

- Python 3.7+
- Flask
- Flask-CORS

## CORS

CORS is enabled for all routes, allowing requests from the React frontend.
