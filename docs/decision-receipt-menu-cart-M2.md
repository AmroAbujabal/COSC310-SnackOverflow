# Proposed decision receipt: shared menu orderability validation

Owner: Al-Munther Bahanshal. Local implementation evidence only; team/lab review pending.

## Integration problem

Cart and checkout both need current menu-item existence, availability and active-state
checks. Duplicating those rules could let the cart accept an item checkout rejects,
or leave one caller using stale state after management changes a menu item.

## Decision and implementation

Add `MenuService.get_orderable_item(restaurant_id, item_id) -> MenuItem`.
It uses `get_menu` to validate the restaurant and menu, finds the item within that
restaurant, and rejects unavailable/deactivated items with BusinessRuleError.
Missing records use the existing NotFoundError family. HTTP mapping remains in the
single upstream DomainError handler; no HTTP exceptions are added to these services.

`CartService.add_item` and `update_quantity` both call this method. Checkout should
call the same method and use its returned current price/name before saving an order.
The checkout caller is a handoff to Amr, not an implemented or verified checkout feature.
The upstream `get_menu` already raises errors instead of returning None, so no duplicate
refactor was necessary.

## Alternatives and tradeoffs

Inline checks in cart/checkout are easy initially but can diverge. Putting availability
checks in a JSON repository mixes business rules with persistence. Keeping the rule
in MenuService gives both callers one domain interface and keeps current data authoritative.

Existing unavailable cart lines remain readable and removable; new additions and
quantity changes are rejected. Customer browsing hides unavailable/inactive items while
management retains them, supporting restoration without deleting IDs.

CartRepository serializes cart mutations within one process and atomically replaces its
JSON after successful validation. This does not coordinate order-file writes or lock
customer/catalog repositories. Cross-file recovery and multiple-worker storage remain
team integration decisions.

## Verifiable evidence

- `tests/test_cart.py::test_shared_orderability_rejects_invalid_items_without_cart_write`
- `tests/test_cart.py::test_regression_item_disabled_after_add_can_be_removed`
- `tests/test_cart.py::test_customer_menu_cart_workflow_and_restart`
- `tests/test_cart.py::test_repository_rollback_and_atomic_replace_failure`
- `tests/test_cart.py::test_repository_stable_ids_unique_active_cart_and_concurrent_adds`
- `tests/test_cart.py::test_deactivated_customer_blocked_in_api_and_service`
- `tests/test_cart.py::test_cart_requires_real_authentication`
- `tests/test_cart.py::test_cart_openapi_documents_contract`

Full regression suite: 125 passed. Peer review, PR/issue links and lab receipt approval
are pending the student's/team's own GitHub and lab workflow.
