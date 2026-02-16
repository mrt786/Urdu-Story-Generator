import os
import sys
import json
import pickle
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'models'))
from trigram_model import StoryGeneratorAPI, TrigramLanguageModel

PORT = 5000
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'trigram_model.pkl')


def ensure_model():
    if os.path.exists(MODEL_PATH):
        api = StoryGeneratorAPI(model_path=MODEL_PATH)
        return api

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


api = ensure_model()


class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type='application/json'):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == '/health' or path == '/':
            self._set_headers(200)
            resp = {'status': 'ok', 'message': 'Backend is running'}
            self.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))
            return

        if path == '/generate':
            prefix = qs.get('prefix', [''])[0]
            try:
                max_length = int(qs.get('max_length', ['500'])[0])
            except Exception:
                max_length = 500
            try:
                temperature = float(qs.get('temperature', ['0.8'])[0])
            except Exception:
                temperature = 0.8

            try:
                result = api.generate(prefix=prefix, max_length=max_length, temperature=temperature)
                self._set_headers(200)
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))
            return

        if path == '/stream':
            prefix = qs.get('prefix', [''])[0]
            try:
                max_length = int(qs.get('max_length', ['500'])[0])
            except Exception:
                max_length = 500
            try:
                temperature = float(qs.get('temperature', ['0.8'])[0])
            except Exception:
                temperature = 0.8

            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            try:
                for token in api.generate_stream(prefix=prefix, max_length=max_length, temperature=temperature):
                    msg = f"data: {token}\n\n"
                    try:
                        self.wfile.write(msg.encode('utf-8'))
                        self.wfile.flush()
                    except BrokenPipeError:
                        break

                try:
                    self.wfile.write(b"event: done\ndata: \n\n")
                    self.wfile.flush()
                except BrokenPipeError:
                    pass
            except Exception as e:
                try:
                    err_msg = f"event: error\ndata: {str(e)}\n\n"
                    self.wfile.write(err_msg.encode('utf-8'))
                    self.wfile.flush()
                except BrokenPipeError:
                    pass

            return

        self._set_headers(404)
        self.wfile.write(json.dumps({'error': 'Not found'}).encode('utf-8'))

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/generate':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            try:
                data = json.loads(body)
            except Exception:
                data = {}

            prefix = data.get('prefix', '')
            max_length = data.get('max_length', 500)
            temperature = data.get('temperature', 0.8)

            try:
                result = api.generate(prefix=prefix, max_length=int(max_length), temperature=float(temperature))
                self._set_headers(200)
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({'error': 'Not found'}).encode('utf-8'))


if __name__ == '__main__':
    server = ThreadingHTTPServer(('0.0.0.0', PORT), Handler)
    print(f"Starting server on http://0.0.0.0:{PORT}")
    print("Endpoints: /health, /generate (GET/POST)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down')
        server.server_close()
