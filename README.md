# SnackOverflow

Backend API for a food-delivery application, built with FastAPI for COSC 310.

## Requirements

- Python 3.11 or newer
- Git

## Setup

Clone the repository:

```bash
git clone https://github.com/AmroAbujabal/COSC310-SnackOverflow.git
cd COSC310-SnackOverflow
```

Create and activate a virtual environment:

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the app

```bash
uvicorn app.main:app --reload
```

The API runs at http://127.0.0.1:8000.

## API endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Health check, returns `{"status": "ok"}` |
| GET | `/docs` | Interactive OpenAPI documentation |

## Data

Representative data is stored as JSON in the `data/` folder.

The data folder can be changed with the `SNACKOVERFLOW_DATA_DIR` environment variable. Tests use this to point at temporary data so the committed files are never modified.

## Running tests

```bash
python -m pytest
```

## Repository structure
app/
core/ configuration (data paths)
main.py FastAPI app and routes
tests/ pytest test suite
docs/ project documentation, including PROVENANCE.md
requirements.txt
pytest.ini

## AI use

AI use is recorded in `docs/PROVENANCE.md`, following the course provenance guide.
