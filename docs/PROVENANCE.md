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

## Entry 5
- Student(s): Kenneth Tandianto
- Artifact: app/services/restaurant_services.py, app/routes/restaurants.py, tests/test_restaurants.py, app/main.py
- Label: AI-GENERATED
- AI tool: ChatGPT
- Purpose: Setting up the restaurant service, get the /restaurant endpoint, and the second test.
- Influence: Used the generated code.
- Validation: Ran the app locally and checked for the /restaurant and /docs in the browser. Ran `python -m pytest -v`, and both the health and restaurant test passed.
- PR: #3

---

## Entry 6
- Student(s): Amro
- Artifact: app/services/exceptions.py, app/models/error.py, app/services/restaurant_services.py, app/routes/restaurants.py, app/main.py, tests/conftest.py, tests/test_restaurant_details.py
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Add the restaurant details endpoint and a shared 404 response for unknown restaurants.
- Influence: Used the generated code and tests. The error design (the service raises a domain error and one handler in main.py maps it to a 404) was proposed by AI and is pending team confirmation.
- Validation: Full test suite run with `python -m pytest` (13 passed). Ran the server and checked /restaurants/1 (200), /restaurants/99 (404), /restaurants/abc (422), and /docs.
- PR: #10

---

## Entry 7
- Student(s): Amro
- Artifact: app/services/restaurant_services.py, app/routes/restaurants.py, tests/test_restaurant_search.py (search/filter); .github/workflows/ci.yml; .github/ISSUE_TEMPLATE/epic.md, user_story.md, task.md; docs/requirements.md
- Label: AI-GENERATED (docs/requirements.md is AI-REVISED: my draft, restructured by AI)
- AI tool: Claude
- Purpose: Add restaurant name search and cuisine filter, CI that runs pytest, the issue templates from Lecture 6, and the requirements document with a traceability matrix.
- Influence: Used the generated code, tests, workflow and templates (epic.md copies the Lecture 6 slide). The requirements doc started from my M1 requirements draft; AI rewrote the stories to the lecture rules and built the traceability matrix. Search parameter names and exact cuisine matching are pending team confirmation.
- Validation: Full test suite run with `python -m pytest` (24 passed on the search branch). Search checked on a running server. CI's first run on PR #24 passed (8 passed on Python 3.11). Template front matter checked.
- PR: #27, #24, #25, #26
