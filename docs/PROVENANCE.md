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
 
 ---
 
## Entry 8 — Menu Models

- **Student(s):** Al-Munther Bahanshal
- **Artifact:** `app/models/menu.py`, `app/models/menu_item.py`
- **Label:** AI-ASSISTED
- **AI tool:** ChatGPT (OpenAI)
- **Purpose:** Create the Menu and MenuItem Pydantic models.
- **Influence:** Used ChatGPT to understand Pydantic, BaseModel, and how the two models should be structured. Used the official Pydantic documentation and ChatGPT suggestions to write and revise the code.
- **Validation:**  Ran pytest successfully. All 19 tests passed. PR review pending.
- **PR:** Pending

---

## Entry 9 — Menu Backend

- **Student(s):** Al-Munther Bahanshal
- **Artifact:** Menu Repository, Menu Service, Menu API routes, JSON data, relationship validation, and automated tests.
- **Label:** AI-GENERATED
- **AI tool:** ChatGPT (OpenAI)
- **Purpose:** Implement menu retrieval functionality following the route → service → repository → JSON architecture.
- **Influence:** Used AI-generated code and guidance for implementation, debugging, and testing. Made adjustments and verified functionality.
- **Validation:** Ran `python -m pytest -v` with 19 tests passing. Tested the API using Swagger UI, including successful retrieval (200) and missing-menu handling (404).
- **PR:** Pending

---


## Entry 10
- Student(s): Amro
- Artifact: tests/test_restaurants.py, docs/requirements.md
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Test that listing restaurants returns an empty list when the stored list is empty, and mark FR1 Finished in the traceability matrix.
- Influence: Used the generated test, which reuses the shared `client` and `data_dir` fixtures from conftest.py.
- Validation: Full test suite run with `python -m pytest` (14 passed before rebasing; 25 after). Confirmed the new test fails when the line that empties the file is removed.
- PR: #29

---

**## Entry 11**
- Student(s): Amro
- Artifact: docs/decision-receipt-404.md, docs/requirements.md, README.md
- Label: AI-ASSISTED
- AI tool: Claude
- Purpose: Record the shared "not found" error design as a Decision Receipt, bring the traceability matrix up to date with merged PRs, and list the search and details endpoints in the README.
- Influence: AI drafted the receipt from the existing code and tests, and updated matrix statuses to match merged PRs #10, #24, #28 and #29. The receipt is marked Proposed until the team confirms it.
- Validation: Checked every file and test name in the receipt exists. Full test suite run with `python -m pytest` (25 passed after rebasing on main).
- PR: #29

---


**## Entry 12**
- Student(s): Kenneth Tandianto
- Artifact: app/models/restaurant_requests.py, app/models/menu_item_requests.py, app/repositories/menu_repository.py, app/repositories/restaurant_repository.py, app/routes/menus.py, app/routes/restaurants.py, app/services/menu_services.py, app/services/restaurant_services.py, tests/test_menu_writes.py, tests/test_restaurant_writes.py
- Label: AI-GENERATED
- AI tool: ChatGPT
- Purpose: Set up request models and implement restaurant and menu-item creation and updating, JSON persistence, stable IDs, and failure-case tests.
- Influence: Used the generated code and modified it.
- Validation: Ran `python -m pytest -v`; 55 tests passed after merging with main. Tested the API using Swagger UI.
- PR: #34


--
## Entry 13 — Text-Only Restaurant Frontend

- **Student(s):** Manveer Sandhu
- **Artifact:** `app/main.py`, `app/frontend/index.html`, `app/frontend/app.js`, `tests/test_frontend.py`
- **Label:** AI-GENERATED
- **AI tool:** GitHub Copilot
- **Purpose:** Add a plain-text restaurant list with search across restaurant information and menu viewing.
- **Influence:** Used AI-generated implementation and revised it to match the requested text-only design.
- **Validation:** Checked text search and menu display in the browser. Ran `python -m pytest -q`; all 36 tests passed.
- **PR:** #33

---

## Entry 14 — Management Front End

- **Student(s):** Manveer Sandhu
- **Artifact:** `app/main.py`, `app/frontend/index.html`, `app/frontend/management.html`, `app/frontend/management.js`, `tests/test_frontend.py`, `README.md`
- **Label:** AI-GENERATED
- **AI tool:** GitHub Copilot
- **Purpose:** Add a management front end to create and edit restaurants and create and edit menu items using the existing API endpoints.
- **Influence:** Used AI-generated page, JavaScript, route, navigation, documentation, and test changes. The page calls the existing restaurant and menu endpoints and handles restaurants that do not have a menu yet.
- **Validation:** Ran `python -m pytest -q` (57 passed). Opened `/management` in the browser and verified the restaurant list and an existing restaurant's menu load.
- **PR:** Pending

---

## Entry 15 — DomainError Hierarchy and One Error Handler

- Student(s): Amro
- Artifact: app/services/exceptions.py, app/main.py, app/services/menu_services.py, app/routes/menus.py, tests/test_errors.py, tests/test_menu_routes.py
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Replace the per-error exception handlers with one DomainError handler that maps NotFoundError to 404, BusinessRuleError to 409 and ForbiddenError to 403, and move the missing-menu 404 from the routes into the service as MenuNotFoundError.
- Influence: Used the generated hierarchy, handler, service change and tests. Wrote the tests first and confirmed they failed before adding the code. Reviewed each change line by line so I can explain it.
- Validation: Ran `python -m pytest -q` (76 passed). Checked that the 404 messages for an unknown restaurant and a missing menu are unchanged.
- PR: #40

---

## Entry 16 — M2 Menu Availability

- **Student(s):** Al-Munther Bahanshal
- **Artifact:** `app/models/menu_item.py`, `app/models/menu_item_requests.py`, `app/routes/menus.py`, `app/services/menu_services.py`, `app/frontend/management.html`, `app/frontend/management.js`, `app/frontend/app.js`, `tests/test_menu_writes.py`, `tests/test_menu_routes.py`
- **Label:** AI-GENERATED
- **AI tool:** ChatGPT / Codex (OpenAI)
- **Purpose:** Implement menu-item availability using the existing route → service → repository → JSON architecture, with management controls and customer-visible status.
- **Influence:** AI generated the availability/deactivation model and request fields, API response schemas, management checkbox, management status labels and filtering unavailable/inactive items from customer browsing, and regression tests. Existing service and repository logic was reused. Reapplied these changes on upstream main (ae4771d), preserving its authentication foundation and DomainError handling. Following Amro's review on PR #43, AI revised customer menu reads to filter unavailable/inactive items in MenuService, added an explicit include_unavailable query for management, removed the redundant customer status label, consolidated exception imports, and added filtering/deactivation regression tests. Human re-review and demonstration are pending.
- **Validation:** Initial menu-only export passed 97 tests. After the PR #43 review fixes and local merge-conflict resolution, Codex reran the full menu-branch suite with cache disabled and isolated temporary data: 125 passed. Tests cover default/explicit filtering on both GET endpoints, full management reads, all-hidden menus, non-mutating service filtering, shared orderability 404/409 behavior, active-state creation/persistence/restoration, strict boolean validation, and OpenAPI query documentation. Both frontend scripts passed `node --check`. Human browser demonstration remains pending.
- **PR:** #43

---

## Entry 17 — Cart and Shared Menu Orderability Validation

- **Student(s):** Al-Munther Bahanshal
- **Artifact:** `app/models/cart.py`, `app/repositories/cart_repository.py`, `app/services/cart_service.py`, `app/routes/cart.py`, `data/carts.json`, `app/services/menu_services.py`, `app/core/config.py`, `app/main.py`, `tests/test_cart.py`, `README.md`, `docs/decision-receipt-menu-cart-M2.md`
- **Label:** AI-GENERATED
- **AI tool:** ChatGPT / Codex (OpenAI)
- **Purpose:** Implement Al-Munther's authenticated cart backend and centralize current menu-item orderability checks for cart and future checkout integration.
- **Influence:** AI generated the cart models, JSON repository, service, API routes, shared MenuService.get_orderable_item helper, focused config/router registration, isolated tests, README API documentation and proposed decision receipt. Used the existing customer/auth foundation and DomainError handler. Checkout, customer/login endpoints and cart frontend remain assigned to teammates; student review and human peer review are pending. After PR #43 introduced default customer-menu filtering, AI updated cart display to explicitly request the complete catalog, preserving disabled lines for removal without weakening add/update orderability checks.
- **Validation:** Codex ran the full pytest suite with cache disabled and isolated temporary data; the original suite passed 125 tests. After merging PR #43 review fixes locally, the combined suite passed 153 tests. Before the compatibility fix, both disabled-item regression cases failed; after cart display requested include_unavailable=True, both passed, including new authenticated API assertions that browsing hides disabled items while GET /cart retains them with orderable=false. Evidence covers Customer → Menu → Cart integration with real JWT authentication, service business rules, current-price totals, cart ownership, inactive customers, quantity validation, persistence/reload, concurrent cart updates, rollback after save failure, and API error documentation. Regression tests verify items disabled after insertion remain removable while additions/quantity changes fail. The complete checkout/order workflow and human browser demonstration remain pending team integration.
- **PR:** #44

---

## Entry 18 — Representative Menu Data

- **Student(s):** Al-Munther Bahanshal
- **Artifact:** `data/menus.json`
- **Label:** AI-GENERATED
- **AI tool:** ChatGPT / Codex (OpenAI)
- **Purpose:** Add representative menu items for the two restaurants that had no sample menu, as requested for local testing and demonstration.
- **Influence:** AI supplied six sample dish names and prices and explicit available/active flags, preserving the original two items and their IDs. An empty menu remains a valid application state.
- **Validation:** Validated the JSON using Menu models, checked unique item IDs and restaurant relationships, and reran the full isolated pytest suite (125 passed).
- **PR:** #43

---

## Entry 19 — Decision Receipt M2.3 (domain errors)

- Student(s): Amro
- Artifact: docs/decision-receipt-m2-3-domain-errors.md, docs/decision-receipt-404.md
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Record the one-hierarchy, one-handler error design from PR #40 as a Decision Receipt, and mark receipt-404 accepted and partly superseded.
- Influence: AI drafted the receipt from the merged code, tests and the team's 2026-11-01 decisions. I checked the reasoning and the options against what we discussed.
- Validation: Checked every cited file and test exists on main. Ran the cited tests (14 passed).
- PR: #42

---

## Entry 20 - Customer Authentication Foundation
- Student(s): Kenneth Tandianto
- Artifact: app/core/config.py, app/core/security.py, app/dependencies, app/dependencies/__init__.py, app/dependencies/auth.py, app/models/customer.py, app/repositories/customer_repository.py, app/data/customers.json, tests/test_customer_repository.py, tests/test_security.py, requirements.txt
- Label: AI-GENERATED
- AI Tool: ChatGPT
- Purpose: Creating the customer model and JSON repository, implemented Argon2 password hashing and verification, added JWT access token creation and decoding, added the get_current_user dependency for authenticated requests, updated application settings for JWT configuration.
- Influence: Used the code generated by AI, and checked it for errors.
- Validation: Checked every file and tests. Ran the tests using 'python -m pytest -v', and returned 68 tests passed.
- PR: #38

---

## Entry 21 - Complete Customer Management and Authentication
- Student(s): Kenneth Tandianto
- Artifact: app/dependencies/auth.py, app/models/customer_requests.py, app/models/customer.py, app/repositories/customer_repository.py, app/repositories/json_repository.py, app/repositories/menu_repository.py, app/repositories/restaurant_repository.py, app/routes/auth.py, app/routes/customers.py, app/routes/menus.py, app/routes/restaurants.py, app/services/customer_services.py, app/services/exceptions.py, app/main.py, tests/conftest.py, tests/test_auth_routes.py, tests/test_customer_repository.py, tests/test_menu_writes.py, tests/test_restaurant_writes.py
- Label: AI-GENERATED
- AI Tool: ChatGPT
- Purpose: Improved and finalized the customer management, authentication, and authorization. Introduced a shared JsonRepository base class, and refactored restaurant, menu, and customer repositories to reuse JSON loading, saving, and ID-generation logic.
- Influence: Used the code generated by AI, and checked it for errors.
- Validation: Checked every file and tests. Ran the tests using 'python -m pytest -v', and returned 95 tests passed.
- PR: #45

## Entry 22 — Orders and Checkout

- Student(s): Amro
- Artifact: app/core/pricing.py, app/models/order.py, app/repositories/order_repository.py, app/services/order_service.py, app/services/checkout_service.py, app/routes/orders.py, app/services/exceptions.py, app/core/config.py, app/main.py, data/orders.json, README.md, tests/conftest.py, tests/test_pricing.py, tests/test_order_models.py, tests/test_order_repository.py, tests/test_order_service.py, tests/test_order_routes.py, tests/test_checkout_service.py, tests/test_checkout_routes.py
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Turn the active cart into a saved order: order storage, GET /orders and GET /orders/{id} (owner or admin only), and POST /checkout, which re-checks every line through get_orderable_item at the current price before saving and clearing the cart.
- Influence: AI wrote the code test-first, one step at a time, following the team's 2026-11-01 decisions (orders visible to the owning customer and admins; one DomainError handler). I chose the design, reviewed each step, and walked through every file before pushing. A code review found two race conditions (reused order ids, double-click creating two orders); both were fixed with a lock and an atomic file write, each with a failing test first.
- Validation: Ran `python -m pytest -q` on top of main after #43 and #44 merged (190 passed). Checkout is tested with fakes and end to end with real JWT tokens, the real cart and menu services, and temporary JSON files, including an item disabled after it was added (409, cart kept) and an empty cart (409).
- PR: #47

---

## Entry 23 — End-to-End Order Flow Test

- Student(s): Amro
- Artifact: tests/test_integration_order_flow.py
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: One integration test of the whole customer journey over HTTP on a copy of the real seed data: register, log in through /auth/login, browse, add to cart, check out, and view the order, plus empty-cart checkout (409), another customer viewing the order (403) and no token (401).
- Influence: AI wrote the test from the merged auth, cart and order routes. I chose what the journey should cover and checked each assertion against the API.
- Validation: Ran `python -m pytest -q` (216 passed; tracked data/ files unchanged). Removed the cart clear from checkout on purpose and confirmed the test fails, then restored it.
- PR: #50

---

## Entry 24 — Customer Frontend Integration

- Student(s): Project contributor (not identified in this session)
- Artifact: app/frontend/index.html, app/frontend/app.js, README.md
- Label: AI-ASSISTED
- AI tool: Copilot SDK in VS Code
- Purpose: Integrate customer registration, authentication, profile, cart, checkout, and order endpoints into the browsing frontend.
- Influence: The AI assistant implemented the frontend against the existing FastAPI contracts and documented the integration. Human review status was not provided.
- Validation: Ran `python -m pytest -q` (224 passed). Verified in a browser using isolated seed data: account registration/sign-in/profile update/sign-out, menu browsing, add/update cart quantity, checkout, and order history/detail.
- PR: Pending.

---

## Entry 25 — Order State Machine

- Student(s): Amro
- Artifact: app/models/order.py, app/repositories/order_repository.py, app/services/order_service.py, app/services/exceptions.py, docs/requirements.md, tests/test_order_models.py, tests/test_order_repository.py, tests/test_order_transitions.py
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: Full order status set and one central transition table (ALLOWED_TRANSITIONS, check_transition, OrderService.change_status) that every status change goes through, so delivery and reports can build on it.
- Influence: I chose the statuses, the allowed moves (one step forward; cancel only while placed or accepted) and that delivery owns out_for_delivery/delivered. AI wrote the code and tests test-first. Reviews led to one name for the lock and a typed table; a review also found two existing checkout risks (undo deleting an accepted order, reused ids), left for the reliability work.
- Validation: Ran `python -m pytest -v` (259 passed; data/ unchanged). Allowed preparing → cancelled on purpose and confirmed the tests fail, then restored it.
- PR: #56

---

## Entry 26 — Order Lifecycle Endpoints

- Student(s): Amro
- Artifact: app/models/order_requests.py, app/routes/orders.py, app/services/order_service.py, app/services/exceptions.py, app/repositories/order_repository.py, README.md, docs/requirements.md, tests/test_order_service.py, tests/test_order_routes.py, tests/test_order_repository.py
- Label: AI-GENERATED
- AI tool: Claude
- Purpose: PATCH /orders/{id}/status for the restaurant's owner or an admin, POST /orders/{id}/cancel for the customer or an admin, and GET /restaurants/{id}/orders so staff can find the orders they manage. Status changes go through OrderService.change_status.
- Influence: I decided that the PATCH only accepts accepted/preparing/ready/cancelled so out_for_delivery and delivered stay with the delivery flow (driver assigned first), that cancel is only for the customer or an admin, and to add the restaurant order list after a review showed owners could not find their orders. AI wrote the code and tests test-first and reused ensure_owner_access and get_order for the access checks. Reviews trimmed duplicate tests and made the 403 message neutral; a security review found nothing.
- Validation: Ran `python -m pytest -v` (299 passed; data/ unchanged). Removed each access check on purpose (ownership on PATCH, own-order on cancel, ownership on the list) and confirmed tests fail each time, then restored.
- PR: Pending
