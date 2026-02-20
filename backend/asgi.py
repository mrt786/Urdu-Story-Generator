from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'models'))
from trigram_model import StoryGeneratorAPI

ROOT = os.path.dirname(__file__)
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'trigram_model.pkl')


def ensure_model():
    if os.path.exists(MODEL_PATH):
        return StoryGeneratorAPI(model_path=MODEL_PATH)
    return StoryGeneratorAPI()


api = ensure_model()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/health')
async def health():
    return JSONResponse({'status': 'ok', 'message': 'Backend is running'})


@app.get('/generate')
async def generate_get(prefix: str = '', max_length: int = 500, temperature: float = 0.8):
    try:
        result = api.generate(prefix=prefix, max_length=max_length, temperature=temperature)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)


@app.post('/generate')
async def generate_post(request: Request):
    body = await request.json()
    prefix = body.get('prefix', '')
    max_length = int(body.get('max_length', 500))
    temperature = float(body.get('temperature', 0.8))
    try:
        result = api.generate(prefix=prefix, max_length=max_length, temperature=temperature)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)


@app.get('/stream')
async def stream(prefix: str = '', max_length: int = 500, temperature: float = 0.8):
    async def event_generator():
        try:
            for token in api.generate_stream(prefix=prefix, max_length=max_length, temperature=temperature):
                yield f"data: {token}\n\n"
            yield "event: done\ndata: \n\n"
        except Exception as e:
            yield f"event: error\ndata: {str(e)}\n\n"

    return StreamingResponse(event_generator(), media_type='text/event-stream')
