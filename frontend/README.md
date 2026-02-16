# Frontend - Urdu Story Generator

Simple React frontend for the Urdu Story Generator API.

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start the Frontend

```bash
npm start
```

The frontend will open at `http://localhost:3000`

## How it Works

1. Enter a starting text in Urdu (optional)
2. Adjust maximum length (1-2000 characters)
3. Adjust temperature (0.1-2.0):
   - Lower values = more consistent output
   - Higher values = more creative/random output
4. Click "Generate Story" to create

## Environment Requirements

- Node.js 14+ and npm

## Configuration

The frontend expects the backend API at `http://localhost:5000`
(configured in package.json proxy setting)
