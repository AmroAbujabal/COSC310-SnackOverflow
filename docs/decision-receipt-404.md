# Decision Receipt: one shared "not found" error

- Status: Proposed (team to confirm at the next meeting)
- Owner: Amro
- Date: 2026-10-14
- Related: FR5, US 1.3, PR #10

## Context

`GET /restaurants/{restaurant_id}` must answer 404 when no restaurant has that id. The menu routes (Al-Munther) and the update routes (Kenneth) will look up a restaurant the same way, so they need the same answer for an unknown id. If each route builds its own 404, the error body and the Swagger docs will drift apart.

## Options considered

1. Each route checks for `None` and raises `HTTPException(404)` itself.
2. The service raises a domain error, `RestaurantNotFoundError`, and one exception handler in `app/main.py` turns it into a 404.

## Decision

Option 2.

- The service (`RestaurantService.get_restaurant`) raises `RestaurantNotFoundError` when the repository returns `None`.
- `app/main.py` has one handler that returns `404` with `{"detail": "Restaurant <id> not found"}`.
- Routes that can return it list `responses={404: {"model": ErrorResponse, ...}}` so Swagger shows the error shape.

## Why

- The service stays free of HTTP: it reports *what* went wrong, and only the web layer decides the status code (the Route/Service split from Receipt M0).
- Every route gets the same 404 body without repeating code.
- The service rule can be tested without a web request.

## Consequences

- Menu and update routes call `get_restaurant()` (or raise `RestaurantNotFoundError` themselves) instead of writing their own 404.
- A new kind of "not found" (e.g. a menu item) gets its own error class and its own handler in `app/main.py`, following the same pattern.
- A non-integer id is still rejected by FastAPI with 422 before the service runs.

## Evidence

- Code: `app/services/exceptions.py`, `app/services/restaurant_services.py`, `app/main.py`, `app/models/error.py`
- Tests: `tests/test_restaurant_details.py::test_unknown_restaurant_returns_404`, `::test_service_raises_for_unknown_restaurant`, `::test_non_integer_id_returns_422`, `::test_docs_list_the_404_response`
