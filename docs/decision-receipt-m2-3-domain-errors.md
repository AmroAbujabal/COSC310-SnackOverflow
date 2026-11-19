# Decision Receipt M2.3: one domain-error hierarchy, one handler

- Status: Accepted (PR #40, reviewed and approved by Al-Munther, merged 2026-11-16)
- Owner: Amro
- Date: 2026-11-18
- Related: Issue #39, PR #40, PR #36. Supersedes the "one handler per error" consequence of `docs/decision-receipt-404.md`.

## Context

In M1, services raised `RestaurantNotFoundError` and `MenuItemNotFoundError`, and `app/main.py` had one exception handler for each. The menu routes still raised `HTTPException(404)` themselves when a restaurant had no menu.

M2 adds many more failures: carts, availability, checkout, orders, and roles. These fall into three kinds:

- something doesn't exist (404)
- the request is valid, but the current data doesn't allow it, e.g. an unavailable item or an empty cart (409)
- the user is logged in but isn't allowed to do this (403)

Keeping the M1 pattern would mean adding a new handler to `main.py` for every new error class.

## Options considered

1. **Keep one handler per error class.** This works, but `main.py` grows with every feature. A missed handler turns a business error into a 500, and there's no test that catches it.
2. **Raise `HTTPException` in services or routes.** That's fast to write, but services then depend on HTTP. Business rules can't be tested without a web request, and each author writes their own error body.
3. **One `DomainError` hierarchy and one handler.** Services raise an error from a small family. A single handler maps each family to a status code.

## Decision

Option 3.

- `app/services/exceptions.py` defines `DomainError` and three families:
  - `NotFoundError` → 404
  - `BusinessRuleError` → 409
  - `ForbiddenError` → 403
- Specific errors inherit from a family. For example, `RestaurantNotFoundError`, `MenuNotFoundError` and `MenuItemNotFoundError` all inherit from `NotFoundError`.
- `app/main.py` has one `@app.exception_handler(DomainError)`, which looks up the family in `STATUS_CODES`. The response body is `{"detail": str(exc)}`, the same shape FastAPI uses, so the frontend handles every error one way.
- If a `DomainError` belongs to no family, the handler logs it and returns `500 {"detail": "Internal server error"}`. That means a missing mapping is our bug, and the internal message isn't shown to the client.
- The menu routes no longer raise `HTTPException`. `MenuService.get_menu` raises `MenuNotFoundError` instead (this folds in PR #36).

## Why

- **Adding an error no longer needs a change in `main.py`.** A new error class only has to pick a family. The handler is written once.
- **Services stay free of HTTP.** They say *what* went wrong, and the web layer decides the status code. This keeps the route/service split from Receipt M0, and business rules can be tested by calling the service directly.
- **409 rather than 422 for business rules.** 422 means the request itself is malformed, and FastAPI and Pydantic already return it. A business-rule failure depends on the *current state* of the data: the same request could succeed tomorrow. That is what 409 Conflict means.
- **No domain `ValidationError` family.** Pydantic's 422 already covers bad input. A second validation path would only duplicate it.

## Consequences

- New errors (cart, availability, checkout, orders) subclass a family. They don't touch `main.py`.
- `docs/decision-receipt-404.md` is still correct about *where* a 404 comes from: the service raises it. Its line saying each new "not found" gets "its own handler in `app/main.py`" no longer applies.
- **401 stays an `HTTPException`** in `app/dependencies/auth.py` (`get_current_user`). It needs the `WWW-Authenticate` header, and it's purely an HTTP concern. It isn't a business rule.
- 422 for malformed input is unchanged.
- Status codes and messages for every M1 endpoint are unchanged. PR #40 changed no existing test assertion; it only added new tests, and all M1 tests still passed. That is the regression evidence.

## Evidence

- Code: `app/services/exceptions.py`, `app/main.py` (`STATUS_CODES`, `domain_error_handler`), `app/services/menu_services.py`, `app/routes/menus.py`
- Tests:
  - `tests/test_errors.py::test_domain_error_maps_to_status_code`: parametrized, one case per family
  - `tests/test_errors.py::test_unmapped_domain_error_is_a_server_error`
  - `tests/test_errors.py::test_handler_is_registered_for_domain_error`
  - `tests/test_menu_routes.py::test_restaurant_without_menu_is_404`
  - `tests/test_menu_routes.py::test_service_raises_menu_not_found`
