import asyncio
import json

import pytest

from app.main import app, domain_error_handler
from app.services.exceptions import (
    BusinessRuleError,
    DomainError,
    ForbiddenError,
    MenuItemNotFoundError,
    RestaurantNotFoundError,
)


@pytest.mark.parametrize(
    "error, status_code, detail",
    [
        (RestaurantNotFoundError(7), 404, "Restaurant 7 not found"),
        (MenuItemNotFoundError(1, 5), 404, "Menu item 5 not found for restaurant 1"),
        (BusinessRuleError("Item 3 is unavailable"), 409, "Item 3 is unavailable"),
        (ForbiddenError("Account is deactivated"), 403, "Account is deactivated"),
    ],
    ids=["restaurant_not_found", "menu_item_not_found", "business_rule", "forbidden"],
)
def test_domain_error_maps_to_status_code(error, status_code, detail):
    response = asyncio.run(domain_error_handler(None, error))

    assert response.status_code == status_code
    assert json.loads(response.body) == {"detail": detail}


def test_unmapped_domain_error_is_a_server_error():
    # A DomainError subclass missing from the map is a bug in our code, not the client's.
    response = asyncio.run(domain_error_handler(None, DomainError("oops")))

    assert response.status_code == 500
    # Internal message stays out of the response.
    assert json.loads(response.body) == {"detail": "Internal server error"}


def test_handler_is_registered_for_domain_error():
    assert app.exception_handlers[DomainError] is domain_error_handler
