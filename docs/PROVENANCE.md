# AI Provenance Log

This file records how generative AI was used in work that is part of this project, following the course's Generative AI Use and Provenance Guide.

Labels: AI-GENERATED, AI-ASSISTED, AI-REVISED, NO-AI

Each team member adds their own entries in the same PR as the work they describe. Newest entries go at the bottom.

---

## Entry 1

- Student(s): Amro
- Artifact: requirements.txt, pytest.ini, app/main.py, tests/test_health.py
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Set up the initial FastAPI project structure, the /health endpoint, and the first test.
- Influence: Used the generated setup and code as the project base.
- Validation: Ran the app locally and checked /health and /docs in the browser. Ran `python -m pytest` and the health test passed.
- PR: #1

## Entry 2

- Student(s): Amro
- Artifact: app/core/config.py, tests/test_config.py, README.md
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Add configurable data path and write the full README.
- Influence: Used the generated config module, tests, and README content.
- Validation: Ran `python -m pytest` and all tests passed. Followed the README setup steps to confirm they work.
- PR: #2

## Entry 3

- Student(s): Amro
- Artifact: app/models/restaurant.py, app/repositories/restaurant_repository.py, tests/test_restaurant_repository.py
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Add the repository layer the architecture requires, so services stop reading files directly.
- Influence: Used the generated repository, model, and tests. Shape (class taking Settings, Pydantic models, one file per entity) was decided by the team before implementation.
- Validation: Ran `python -m pytest` and all 7 tests passed.
- PR: #5


## Entry 4
- Student(s): Al-Munther
- Artifact: data/restaurants.json
- Label: AI-ASSISTED
- AI tool: Claude
- Purpose: Learn JSON syntax and the restaurant field layout for the data file.
- Influence: Claude explained the JSON structure and gave one example line. I wrote all restaurant names, addresses, ratings, and values myself.
- Validation: Checked the file is valid JSON and matches the agreed fields.
- PR: #6

---

## Entry 2
- Student(s): Kenneth Tandianto
- Artifact: app/services/restaurant_services.py, app/routes/restaurants.py, tests/test_restaurants.py, app/main.py
- Label: AI-GENERATED
- AI tool: ChatGPT
- Purpose: Setting up the restaurant service, get the /restaurant endpoint, and the second test.
- Influence: Used the generated code.
- Validation: Ran the app locally and checked for the /restaurant and /docs in the browser. Ran `python -m pytest -v`, and both the health and restaurant test passed.
- PR: #3

## Entry 6

- Student(s): Amro
- Artifact: app/routes/restaurants.py (response_model), README.md
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Declare the Restaurant model as the /restaurants response model and bring the README up to date for M0 (endpoints, data file, repository structure).
- Influence: Used the generated change and README text.
- Validation: Ran `python -m pytest` and all tests passed. Checked /restaurants and the Restaurant schema in /docs.
- PR: #7
