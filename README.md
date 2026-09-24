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
| GET | `/restaurants` | List all restaurants (id, name, cuisine, address, rating) |
| GET | `/docs` | Interactive OpenAPI documentation |

## Data

Representative restaurant data is stored in `data/restaurants.json`.

The data folder can be changed with the `SNACKOVERFLOW_DATA_DIR` environment variable. Tests point the app at a temporary folder so the committed data is never modified.

## Running tests

```bash
python -m pytest
```

## Repository structure

```
app/
  main.py        FastAPI app, registers the routers
  routes/        HTTP endpoints (routes -> services)
  services/      business logic (services -> repositories)
  repositories/  reads and writes the JSON data files
  models/        Pydantic models (the API data contract)
  core/          configuration (data paths)
data/            representative JSON data
tests/           pytest test suite
docs/            project documentation, including PROVENANCE.md
scrum/           team agreement
requirements.txt
pytest.ini
```

## AI use

AI use is recorded in `docs/PROVENANCE.md`, following the course provenance guide.
