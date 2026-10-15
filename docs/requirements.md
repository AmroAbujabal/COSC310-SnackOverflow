# SnackOverflow Requirements (M1)

Living document. Items marked **(confirm)** are proposals waiting for a team decision. Teammates' stories and endpoints are marked **owner to confirm** until the owner rewrites them in their own issue.

## 1. Epic

**EPIC-01 Restaurant Discovery & Menu Browsing.** Customers can find restaurants and inspect their menus. Restaurant owners can maintain restaurant and menu data. Authentication is out of scope for M1, so "restaurant owner" is a role in the stories, not an enforced permission.

Definition of done:
- Customers can list, search and filter restaurants and open one restaurant's details.
- Customers can view a restaurant's menu and menu items.
- Restaurant owners can create/update restaurants and add/update menu items; changes persist across a restart.
- Unknown restaurants/items and invalid input are handled with documented errors.
- Endpoints are documented in OpenAPI, follow route → service → repository → JSON, and are covered by automated tests.

## 2. User stories

| Story | Statement | Owner | Issue | Priority |
|---|---|---|---|---|
| US 1.1 View restaurants | As a customer, I want to see all the restaurants on SnackOverflow, so that I can choose where to order from. | Amro | #11 | Must |
| US 1.2 Search and filter restaurants | As a customer, I want to find restaurants by name or by type of food, so that I can quickly find something I feel like eating. | Amro | #9 | Must |
| US 1.3 View restaurant details | As a customer, I want to see one restaurant's details, so that I can decide whether to order from it. | Amro | #8 | Must |
| US 1.4 View a restaurant's menu | As a customer, I want to view a restaurant's menu and its items, so that I know what I can order. | Al-Munther (owner to confirm) | — | Must |
| US 2.1 Create and update a restaurant | As a restaurant owner, I want to add and edit my restaurant's information, so that customers see accurate details. | Kenneth (owner to confirm) | — | Must |
| US 2.2 Add and update menu items | As a restaurant owner, I want to add and edit menu items, so that my menu stays current. | Kenneth (owner to confirm) | — | Must |

Acceptance criteria and measures of success live in each story's issue, so there is one source of truth. Every story is checked against INVEST (Independent, Negotiable, Valuable, Estimable, Small, Testable) and split into 2–4 hour tasks.

## 3. Business and domain rules → system requirements

| BR_ID | Business / domain rule | System requirement ("the system shall…") | Verified by |
|---|---|---|---|
| BR1 | Every restaurant has a unique, stable identifier. | The system shall assign a unique id on create and never change or reuse it, including after a restart. | Create and restart tests (Kenneth) |
| BR2 | A restaurant must have a name, cuisine and address. **(confirm required fields)** | The system shall reject a create/update with a missing or empty required field (422). | Create/update failure tests (Kenneth) |
| BR3 | A rating, if present, is between 0 and 5. **(confirm range)** | The system shall reject ratings outside the range (422). | Validation test |
| BR4 | A menu item belongs to exactly one existing restaurant. | The system shall reject adding an item for an unknown restaurant (404) and store the restaurant id on every item. | Menu tests, data-consistency test |
| BR5 | A menu item price is not negative. **(confirm: is zero allowed?)** | The system shall reject negative prices (422). | Validation test |
| BR6 | The backend is authoritative. | The system shall validate every rule in the service/Pydantic layer, never only in the frontend. | API-level tests |
| BR7 | Stored data stays valid. | The system shall not store a menu item that references a restaurant that does not exist. | Data-consistency test over committed data |
| BR8 | Automated tests must not change committed data. | Tests shall use `tmp_path` and `dependency_overrides[get_settings]`. | Test fixtures (`tests/conftest.py`) |

### Quality requirements

| QR_ID | Requirement | Measure | Status |
|---|---|---|---|
| QR1 | Restaurant search is fast enough to feel instant. | For 95% of requests on the sample data, restaurant search responds within 1 second. | **(confirm whether to include)** |

## 4. Priority (MoSCoW)

- **Must:** list, search/filter, details (+404), menu view, create/update restaurant, add/update menu item, persistence across restart, tests, CI, README / PROVENANCE / scrum notes, tag and Canvas PDF.
- **Should:** documented error responses on every endpoint; QR1.
- **Could:** extra filters (e.g. minimum rating).
- **Won't now:** authentication, authorization, registration, carts, checkout, orders, deliveries.

## 5. Requirements traceability matrix

Columns follow the Lecture 5 format (BR → FR → test case → status). Test Case IDs are real test names (`file::test`). Update the row in the same PR that adds or changes the tests.

Status: **Finished** (merged to `main`), **In Progress** (open PR), **Not Started**.

| BR_ID | FR_ID | Requirement | Story | Endpoint | Route → Service → Repository | Priority | Test Case ID | Owner | Status | Comments |
|---|---|---|---|---|---|---|---|---|---|---|
| BR8 | FR1 | List restaurants | US 1.1 | `GET /restaurants` | `restaurants()` → `list_restaurants()` → `list_all()` | Must | `test_restaurants.py::test_get_restaurants`, `test_restaurant_repository.py::test_list_all_returns_every_restaurant` | Amro | In Progress | Built in M0. Empty-store test planned (#13). |
| BR6 | FR2 | Search by name | US 1.2 | `GET /restaurants?name=` | `restaurants()` → `list_restaurants(name)` → `list_all()` | Must | `test_restaurant_search.py::test_search_and_filter[name match]`, `[name ignores case and matches part]`, `[no match]`, `[blank name ignored]` | Amro | In Progress | Param names pending team confirmation. |
| BR6 | FR3 | Filter by cuisine | US 1.2 | `GET /restaurants?cuisine=` | `restaurants()` → `list_restaurants(cuisine)` → `list_all()` | Must | `test_restaurant_search.py::test_search_and_filter[cuisine ignores case]`, `[cuisine needs exact match]`, `[filters combine]`, `[combined with no match]` | Amro | In Progress | Exact vs partial cuisine match **(confirm)**. |
| BR1 | FR4 | Restaurant details | US 1.3 | `GET /restaurants/{restaurant_id}` | `restaurant_details()` → `get_restaurant()` → `get()` | Must | `test_restaurant_details.py::test_get_restaurant_returns_its_details`, `test_restaurant_repository.py::test_get_returns_matching_restaurant` | Amro | In Progress | PR #10. |
| BR6 | FR5 | Unknown or invalid restaurant id | US 1.3 | `GET /restaurants/{restaurant_id}` | service raises `RestaurantNotFoundError` → handler in `main.py` → 404 | Must | `test_restaurant_details.py::test_unknown_restaurant_returns_404`, `::test_non_integer_id_returns_422`, `::test_docs_list_the_404_response`, `::test_service_raises_for_unknown_restaurant`, `test_restaurant_repository.py::test_get_returns_none_when_id_is_unknown` | Amro | In Progress | PR #10. Shared 404 reused by menu/update routes **(confirm)**. |
| BR7 | FR6 | View menu and menu items | US 1.4 | `GET /restaurants/{id}/menu` (owner to confirm) | route → menu service → menu repository | Must | — | Al-Munther | Not Started | |
| BR1, BR2, BR3 | FR7 | Create restaurant | US 2.1 | `POST /restaurants` (owner to confirm) | route → service → repository write | Must | — | Kenneth | Not Started | |
| BR1, BR2, BR3 | FR8 | Update restaurant | US 2.1 | `PATCH`/`PUT /restaurants/{id}` (owner to confirm) | route → service → repository write | Must | — | Kenneth | Not Started | |
| BR4, BR5 | FR9 | Add menu item | US 2.2 | `POST /restaurants/{id}/menu` (owner to confirm) | route → service → repository write | Must | — | Kenneth | Not Started | |
| BR4, BR5 | FR10 | Update menu item | US 2.2 | `PATCH /restaurants/{id}/menu/{item_id}` (owner to confirm) | route → service → repository write | Must | — | Kenneth | Not Started | |
| — | FR11 | Health check | — | `GET /health` | route only | Must | `test_health.py::test_health_returns_ok` | Amro | Finished | M0. |
| BR8 | FR12 | Configurable data location | — | — | `get_settings()` | Must | `test_config.py::test_default_data_dir_is_repo_data_folder`, `::test_data_dir_can_be_overridden_with_env_var` | Amro | Finished | M0. |
| BR6 | FR13 | Stored records are validated on load | — | — | `list_all()` builds `Restaurant` models | Must | `test_restaurant_repository.py::test_list_all_rejects_a_record_with_a_missing_field` | Amro | Finished | M0. |
| — | FR14 | CI runs the test suite on every PR | — | — | GitHub Actions (`.github/workflows/ci.yml`) | Must | CI job `tests` | Manveer | In Progress | PR #24. |
