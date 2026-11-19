
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings, get_settings
from app.core.security import create_access_token
from app.main import app
from app.models.cart import Cart, CartAdd, CartLine, CartQuantityUpdate
from app.models.customer import Customer
from app.models.menu_item_requests import MenuItemUpdate
from app.repositories.cart_repository import CartRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.cart_service import CartService
from app.services.exceptions import (
    BusinessRuleError,
    ForbiddenError,
    MenuItemNotFoundError,
    NotFoundError,
)
from app.services.menu_services import MenuService


@pytest.fixture
def cart_context(tmp_path):
    settings = Settings(data_dir=tmp_path)

    restaurants = [
        dict(
            id=i,
            name=f"Cafe {i}",
            cuisine="Other",
            address="Here",
            rating=4,
            owner_id=3,
        )
        for i in (1, 2)
    ]

    menus = [
        dict(
            restaurant_id=1,
            items=[
                dict(item_id=1, restaurant_id=1, name="Soup", price=0.10),
                dict(item_id=2, restaurant_id=1, name="Bread", price=0.20),
                dict(
                    item_id=3,
                    restaurant_id=1,
                    name="Sold out",
                    price=4,
                    available=False,
                ),
                dict(
                    item_id=4,
                    restaurant_id=1,
                    name="Retired",
                    price=5,
                    active=False,
                ),
            ],
        ),
        dict(
            restaurant_id=2,
            items=[
                dict(item_id=5, restaurant_id=2, name="Roll", price=6)
            ],
        ),
    ]

    for name, records in [
        ("restaurants", restaurants),
        ("menus", menus),
        ("customers", []),
        ("carts", []),
    ]:
        (tmp_path / f"{name}.json").write_text(
            json.dumps(records),
            encoding="utf-8",
        )

    customers = CustomerRepository(settings)

    # Create two regular customers for the cart tests.
    for i in (1, 2):
        customers.create(
            Customer(
                id=i,
                name=f"Customer {i}",
                email=f"c{i}@example.com",
                password_hash="not-used-by-token-test",
                address="Here",
            )
        )

    # Create an owner for tests that modify restaurant menus.
    customers.create(
        Customer(
            id=3,
            name="Test Owner",
            email="owner@example.com",
            password_hash="not-used-by-token-test",
            address="Here",
            role="owner",
        )
    )

    menus_service = MenuService(
        MenuRepository(settings),
        RestaurantRepository(settings),
    )

    service = CartService(
        CartRepository(settings),
        customers,
        menus_service,
    )

    return settings, service, menus_service


@pytest.fixture
def cart_client(cart_context):
    settings, _, _ = cart_context

    previous = dict(app.dependency_overrides)
    app.dependency_overrides[get_settings] = lambda: settings

    try:
        with TestClient(app) as client:
            client.headers["Authorization"] = (
                f"Bearer {create_access_token(1, settings)}"
            )
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


@pytest.fixture
def cart_owner_client(cart_context):
    settings, _, _ = cart_context

    previous = dict(app.dependency_overrides)
    app.dependency_overrides[get_settings] = lambda: settings

    try:
        with TestClient(app) as client:
            client.headers["Authorization"] = (
                f"Bearer {create_access_token(3, settings)}"
            )
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)

def add(service, item=1, quantity=1, restaurant=1, customer=1):
    return service.add_item(
        customer,
        CartAdd(
            restaurant_id=restaurant,
            item_id=item,
            quantity=quantity,
        ),
    )


def test_customer_menu_cart_workflow_and_restart(cart_context, cart_client):
    settings, _, _ = cart_context

    assert cart_client.get("/restaurants/1/menu").status_code == 200

    first = cart_client.get("/cart").json()
    assert first["items"] == [] and first["total"] == 0

    assert cart_client.post(
        "/cart/items",
        json=dict(restaurant_id=1, item_id=1, quantity=2),
    ).status_code == 200

    cart_client.post(
        "/cart/items",
        json=dict(restaurant_id=1, item_id=2, quantity=1),
    )

    response = cart_client.patch(
        "/cart/items/1",
        json={"quantity": 3},
    )

    assert response.status_code == 200
    assert response.json()["subtotal"] == response.json()["total"] == 0.5
    assert response.json()["items"][0]["line_total"] == 0.3

    # Reload independent repositories/services, as a restarted app would.
    fresh = CartService(
        CartRepository(settings),
        CustomerRepository(settings),
        MenuService(
            MenuRepository(settings),
            RestaurantRepository(settings),
        ),
    )

    assert fresh.get_or_create_active(1).model_dump() == response.json()
    assert fresh.get_or_create_active(1).id == first["id"]

    assert cart_client.delete("/cart/items/1").status_code == 204
    assert cart_client.get("/cart").json()["total"] == 0.2

    assert cart_client.delete("/cart").status_code == 204

    cleared = cart_client.get("/cart").json()
    assert cleared["id"] == first["id"]
    assert cleared["restaurant_id"] is None

    assert cart_client.post(
        "/cart/items",
        json=dict(restaurant_id=2, item_id=5, quantity=1),
    ).status_code == 200


def test_service_combines_lines_and_recalculates_current_price(cart_context):
    settings, service, _ = cart_context

    add(service, quantity=2)
    view = add(service, quantity=3)

    assert len(view.items) == 1
    assert view.items[0].quantity == 5

    MenuRepository(settings).update_item(
        1,
        1,
        MenuItemUpdate(price=1.235),
    )

    assert service.get_or_create_active(1).total == 6.2


@pytest.mark.parametrize(
    "restaurant,item,error",
    [
        (1, 3, BusinessRuleError),
        (1, 4, BusinessRuleError),
        (1, 999, MenuItemNotFoundError),
        (2, 1, MenuItemNotFoundError),
        (999, 1, NotFoundError),
    ],
)
def test_shared_orderability_rejects_invalid_items_without_cart_write(
    cart_context,
    restaurant,
    item,
    error,
):
    settings, service, menus = cart_context
    before = settings.carts_file.read_bytes()

    with pytest.raises(error):
        menus.get_orderable_item(restaurant, item)

    with pytest.raises(error):
        add(service, item=item, restaurant=restaurant)

    assert settings.carts_file.read_bytes() == before


def test_mixed_restaurants_and_combined_quantity_rollback(cart_context):
    settings, service, _ = cart_context

    add(service, quantity=99)
    before = settings.carts_file.read_bytes()

    for action in (
        lambda: add(service),
        lambda: add(service, item=5, restaurant=2),
    ):
        with pytest.raises(BusinessRuleError):
            action()

        assert settings.carts_file.read_bytes() == before


@pytest.mark.parametrize(
    "quantity",
    [0, -1, 100, 1.5, "2", True, None],
)
def test_invalid_quantities_rejected_at_model_and_api(
    cart_context,
    cart_client,
    quantity,
):
    settings, _, _ = cart_context
    before = settings.carts_file.read_bytes()

    with pytest.raises(ValidationError):
        CartQuantityUpdate(quantity=quantity)

    response = cart_client.post(
        "/cart/items",
        json=dict(restaurant_id=1, item_id=1, quantity=quantity),
    )

    assert response.status_code == 422

    assert cart_client.patch(
        "/cart/items/1",
        json={"quantity": quantity},
    ).status_code == 422

    assert settings.carts_file.read_bytes() == before


def test_api_does_not_trust_customer_ids_prices_or_totals(
    cart_context,
    cart_client,
):
    settings, _, _ = cart_context

    for field in ("customer_id", "unit_price", "total"):
        response = cart_client.post(
            "/cart/items",
            json={
                "restaurant_id": 1,
                "item_id": 1,
                "quantity": 1,
                field: 2,
            },
        )

        assert response.status_code == 422

    cart_client.post(
        "/cart/items",
        json=dict(restaurant_id=1, item_id=1, quantity=1),
    )

    cart_client.headers["Authorization"] = (
        f"Bearer {create_access_token(2, settings)}"
    )

    assert cart_client.get("/cart").json()["items"] == []
    assert cart_client.delete("/cart/items/1").status_code == 404
    assert CartRepository(settings).get_active(1).items[0].quantity == 1


@pytest.mark.parametrize("header", [None, "Bearer invalid"])
def test_cart_requires_real_authentication(cart_client, header):
    cart_client.headers.pop("Authorization", None)

    if header:
        cart_client.headers["Authorization"] = header

    for method, path, body in [
        ("get", "/cart", None),
        ("delete", "/cart", None),
        (
            "post",
            "/cart/items",
            dict(restaurant_id=1, item_id=1, quantity=1),
        ),
        ("patch", "/cart/items/1", {"quantity": 2}),
        ("delete", "/cart/items/1", None),
    ]:
        kwargs = {"json": body} if body else {}
        assert getattr(cart_client, method)(path, **kwargs).status_code == 401


def test_deactivated_customer_blocked_in_api_and_service(
    cart_context,
    cart_client,
):
    settings, service, _ = cart_context

    add(service)

    customers = json.loads(settings.customers_file.read_text())
    customers[0]["is_active"] = False

    settings.customers_file.write_text(
        json.dumps(customers),
        encoding="utf-8",
    )

    before = settings.carts_file.read_bytes()

    assert cart_client.get("/cart").status_code == 401

    for action in (
        lambda: service.get_or_create_active(1),
        lambda: add(service),
        lambda: service.update_quantity(
            1,
            1,
            CartQuantityUpdate(quantity=2),
        ),
        lambda: service.remove_item(1, 1),
        lambda: service.clear(1),
    ):
        with pytest.raises(ForbiddenError):
            action()

    assert settings.carts_file.read_bytes() == before

    with pytest.raises(NotFoundError):
        service.get_or_create_active(999)


@pytest.mark.parametrize("field", ["available", "active"])
def test_regression_item_disabled_after_add_can_be_removed(
    cart_context,
    cart_client,
    field,
):
    settings, service, menus = cart_context

    add(service)

    MenuRepository(settings).update_item(
        1,
        1,
        MenuItemUpdate(**{field: False}),
    )

    assert service.get_or_create_active(1).items[0].orderable is False

    # Customer browsing hides disabled items, but an existing cart must stay readable.
    for endpoint in (
        "/restaurants/1/menu",
        "/restaurants/1/menu/items",
    ):
        response = cart_client.get(endpoint)

        assert response.status_code == 200

        items = (
            response.json()["items"]
            if endpoint.endswith("/menu")
            else response.json()
        )

        assert 1 not in [item["item_id"] for item in items]

    response = cart_client.get("/cart")

    assert response.status_code == 200
    assert response.json()["items"][0]["item_id"] == 1
    assert response.json()["items"][0]["orderable"] is False
    assert response.json()["total"] == 0.1

    before = settings.carts_file.read_bytes()

    for action in (
        lambda: add(service),
        lambda: service.update_quantity(
            1,
            1,
            CartQuantityUpdate(quantity=2),
        ),
    ):
        with pytest.raises(BusinessRuleError):
            action()

    assert cart_client.post(
        "/cart/items",
        json=dict(restaurant_id=1, item_id=1, quantity=1),
    ).status_code == 409

    assert settings.carts_file.read_bytes() == before

    with pytest.raises(BusinessRuleError):  # Checkout calls this same helper.
        menus.get_orderable_item(1, 1)

    assert cart_client.delete("/cart/items/1").status_code == 204
    assert service.get_or_create_active(1).items == []


def test_deleted_item_does_not_prevent_removal_or_clear(cart_context):
    settings, service, _ = cart_context

    add(service)

    settings.menus_file.write_text("[]", encoding="utf-8")

    service.remove_item(1, 1)
    assert service.get_or_create_active(1).items == []

    service.clear(1)


def test_repository_stable_ids_unique_active_cart_and_concurrent_adds(
    cart_context,
):
    settings, service, _ = cart_context

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda _: add(service), range(12)))

    repo = CartRepository(settings)

    assert len(repo.list_all()) == 1
    assert repo.get_active(1).items[0].quantity == 12

    first_id = repo.get_active(1).id

    service.clear(1)

    assert service.get_or_create_active(1).id == first_id
    assert service.get_or_create_active(2).id > first_id

    with pytest.raises(ValueError):
        with repo.transaction() as carts:
            carts.append(Cart(id=999, customer_id=1))

    assert len(repo.list_all()) == 2


def test_repository_rollback_and_atomic_replace_failure(
    cart_context,
    monkeypatch,
):
    settings, service, _ = cart_context

    add(service)

    before = settings.carts_file.read_bytes()
    repo = CartRepository(settings)

    with pytest.raises(RuntimeError):
        with repo.transaction() as carts:
            carts.clear()
            raise RuntimeError("Failed operation")

    assert settings.carts_file.read_bytes() == before

    def fail_replace(*args):
        raise OSError("Disk failure")

    monkeypatch.setattr(Path, "replace", fail_replace)

    with pytest.raises(OSError):
        service.clear(1)

    assert settings.carts_file.read_bytes() == before
    assert not settings.carts_file.with_suffix(".tmp").exists()


def test_cart_storage_rejects_invalid_relationships(cart_context):
    settings, _, _ = cart_context

    with pytest.raises(ValidationError):
        Cart(
            id=1,
            customer_id=1,
            items=[CartLine(item_id=1, quantity=1)],
        )

    with pytest.raises(ValidationError):
        Cart(
            id=1,
            customer_id=1,
            restaurant_id=1,
            items=[CartLine(item_id=1, quantity=1)] * 2,
        )

    settings.carts_file.write_text(
        '[{"id":1,"customer_id":1},{"id":1,"customer_id":2}]',
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        CartRepository(settings).list_all()


def test_cart_openapi_documents_contract(cart_client):
    schema = cart_client.get("/openapi.json").json()

    for path in (
        "/cart",
        "/cart/items",
        "/cart/items/{item_id}",
    ):
        for operation in schema["paths"][path].values():
            assert operation["security"]
            assert {"401", "403", "404", "409"} <= set(
                operation["responses"]
            )

    assert (
        schema["paths"]["/cart"]["get"]["responses"]["200"]
        ["content"]["application/json"]["schema"]["$ref"]
        .endswith("CartView")
    )


@pytest.mark.parametrize("active", [False, True])
def test_menu_deactivation_api_persists(
    cart_context,
    cart_owner_client,
    active,
):
    settings, _, _ = cart_context

    response = cart_owner_client.patch(
        "/restaurants/1/menu/items/1",
        json={"active": active},
    )

    assert response.status_code == 200
    assert response.json()["active"] is active

    assert MenuRepository(settings).get(1).items[0].active is active

    assert cart_owner_client.patch(
        "/restaurants/1/menu/items/1",
        json={"active": "false"},
    ).status_code == 422
