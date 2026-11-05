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
The restaurant browsing page is at http://127.0.0.1:8000/ and the management front end is at http://127.0.0.1:8000/management.

## API endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Health check, returns `{"status": "ok"}` |
| GET | `/restaurants` | List all restaurants (id, name, cuisine, address, rating) |
| GET | `/restaurants?name=&cuisine=` | Search by part of the name and/or filter by exact cuisine (both ignore case); no match returns `[]` |
| GET | `/restaurants/{restaurant_id}` | One restaurant's details; `404` with `{"detail": ...}` if the id is unknown |
| GET | `/docs` | Interactive OpenAPI documentation |
| POST | `/restaurants` | Create a restaurant |
| PATCH | `/restaurants/{restaurant_id}` | Update a restaurant |
| GET | `/restaurants/{restaurant_id}/menu` | A restaurant's menu; `404` if the restaurant is unknown or has no menu |
| GET | `/restaurants/{restaurant_id}/menu/items` | The items on a restaurant's menu; same `404`s as above |
| POST | `/restaurants/{restaurant_id}/menu/items` | Add a menu item |
| PATCH | `/restaurants/{restaurant_id}/menu/items/{item_id}` | Update a menu item |

The management front end can create and edit restaurants and create and edit their menu items using these API endpoints.

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
