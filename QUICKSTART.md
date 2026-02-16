# Urdu Story Generator - Full Stack Application

Complete NLP application for generating Urdu stories using a Trigram Language Model.

## Project Structure

```
├── backend/                    # Flask API
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt        # Python dependencies
│   └── README.md              # Backend documentation
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── App.js             # Main React component
│   │   ├── App.css            # Styling
│   │   └── index.js           # Entry point
│   ├── public/
│   │   └── index.html         # HTML template
│   ├── package.json           # Node dependencies
│   └── README.md              # Frontend documentation
├── models/                     # Machine learning models
│   ├── trigram_model.py       # Trigram model implementation
│   ├── trigram_model.pkl      # Trained model (required)
│   └── test1.ipynb            # Testing notebook
├── PreProcessing/             # Text preprocessing
│   ├── preprocessing.py
│   └── Preprocessed_documents/
├── Tokenization/              # Tokenization (BPE)
│   ├── BPE.py
│   ├── vocab.json
│   ├── merges.txt
│   └── encoded_dataset.txt
└── Scraping/                  # Web scraping
    ├── urdupoint.py
    └── Documents/
```

## Quick Start

### Option 1: Run Backend & Frontend Separately (Recommended)

#### Terminal 1 - Start Backend:
```bash
cd backend
pip install -r requirements.txt
python app.py
```
Backend will run at: `http://localhost:5000`

#### Terminal 2 - Start Frontend:
```bash
cd frontend
npm install
npm start
```
Frontend will open at: `http://localhost:3000`

### Option 2: Quick Test via Command Line

Test the backend API directly:
```bash
# Test health check
curl http://localhost:5000/health

# Generate a story
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prefix": "ایک دن",
    "max_length": 500,
    "temperature": 0.8
  }'
```

## Prerequisites

### Backend Requirements:
- Python 3.7+
- Flask, Flask-CORS
- Trained model file: `models/trigram_model.pkl`

### Frontend Requirements:
- Node.js 14+
- npm

## Installation

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

## Running the Application

### Start Backend (Terminal 1):
```bash
cd backend
python app.py
```
Expected output:
```
Starting Urdu Story Generator Backend...
API available at http://localhost:5000
Frontend should be configured to call: http://localhost:5000/generate
 * Running on http://0.0.0.0:5000
```

### Start Frontend (Terminal 2):
```bash
cd frontend
npm start
```
This will automatically open `http://localhost:3000` in your browser.

## Features

✅ **Simple Web Interface** - Easy-to-use React frontend
✅ **RESTful API** - Flask backend with CORS support
✅ **Urdu Text Support** - Full Unicode support for Urdu text
✅ **Configurable Generation** - Control length and creativity
✅ **Real-time Generation** - Fast story generation
✅ **Copy to Clipboard** - Easy story sharing

## How to Use

1. **Enter Starting Text** (optional)
   - Type Urdu text to start the story
   - If empty, story starts with learned patterns

2. **Adjust Parameters**
   - **Max Length**: How long the story should be (1-2000)
   - **Temperature**: Creativity level (0.1-2.0)
     - 0.1-0.5: More consistent, logical output
     - 0.8: Balanced (recommended)
     - 1.5-2.0: More random, creative output

3. **Generate**
   - Click "Generate Story" button
   - Wait for the model to generate the complete story
   - Copy the result if desired

## API Documentation

### Endpoints

#### 1. Health Check
```
GET /health
```

#### 2. Generate Story
```
POST /generate
Content-Type: application/json

{
  "prefix": "ایک دن",
  "max_length": 500,
  "temperature": 0.8
}
```

Consider reading individual README files in `backend/` and `frontend/` for detailed documentation.

## Troubleshooting

### Backend won't start:
- Ensure `trigram_model.pkl` exists in the `models/` folder
- Check Python version is 3.7+
- Verify all dependencies installed: `pip install -r requirements.txt`

### Frontend can't connect:
- Ensure backend is running on port 5000
- Check browser console for errors
- Verify CORS is working (check Flask logs)

### Model file missing:
You need to train the model first. Use the existing scripts in `models/` directory.

## Development Notes

- Backend uses Flask with CORS enabled
- Frontend uses React with direct proxy to backend
- Model is loaded once at startup for performance
- Stories are generated character-by-character using the trigram model

## Next Steps

- Add authentication if needed
- Implement model training endpoint
- Add story history/caching
- Deploy to cloud (Heroku, AWS, etc.)
- Add additional language models
- Implement advanced features (story length control, tone/style selection)

---

**Made for NLP Assignment**
