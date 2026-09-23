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
- PR: 
