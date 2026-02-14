# NLP Assignment 1 - UrduStory Generator

Currently, This project scrapes moral stories from UrduPoint and saves them as text files.

## Setup Instructions

### 1. Create a Virtual Environment
To isolate the project dependencies, create a virtual environment:

```bash
python -m venv A1
```

### 2. Activate the Virtual Environment
Activate the virtual environment:

- On Windows (PowerShell):
  ```powershell
  .\A1\Scripts\Activate.ps1
  ```
- On Windows (Command Prompt):
  ```cmd
  A1\Scripts\activate.bat
  ```
- On macOS/Linux:
  ```bash
  source A1/bin/activate
  ```

### 3. Install Requirements
Install the required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Run the Scraper
Execute the scraping script:

```bash
python Scrapping/urdupoint.py
```

This will scrape the stories and save them in the `Scrapping/` directory as `Document 1.txt`, `Document 2.txt`, etc.

## Notes
- The script runs in headless mode for automation.
- Ensure you have Python 3.8+ installed.
- The virtual environment files are ignored in `.gitignore` to avoid committing them to Git.