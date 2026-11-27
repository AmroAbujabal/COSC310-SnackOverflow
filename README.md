# SnackOverflow

Backend API for a food-delivery application, built with FastAPI for COSC 310.

## Requirements

- Python 3.11 or newer
- Git

## Setup

Clone the repository:

```bash
git clone https://github.com/AmroAbujabal/COSC310-SnackOverflow.git
cd COSC310-SnackOverflow
```

Create and activate a virtual environment:

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the app

```bash
uvicorn app.main:app --reload
```

The API runs at http://127.0.0.1:8000.

The restaurant browsing page is at http://127.0.0.1:8000/ and the management front end is at http://127.0.0.1:8000/management.

## API endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Health check, returns `{"status": "ok"}` |
| POST | `/auth/register` | Register a customer account |
| POST | `/auth/login` | Sign in with an email and password to receive a bearer token |
| GET/PATCH/DELETE | `/customers/me` | View, update, or deactivate the signed-in customer's account |
| GET | `/restaurants` | List all restaurants (id, name, cuisine, address, rating) |
| GET | `/restaurants?name=&cuisine=` | Search by part of the name and/or filter by exact cuisine (both ignore case); no match returns `[]` |
| GET | `/restaurants/{restaurant_id}` | One restaurant's details; `404` with `{"detail": ...}` if the id is unknown |
| GET | `/docs` | Interactive OpenAPI documentation |
| POST | `/restaurants` | Create a restaurant |
| PATCH | `/restaurants/{restaurant_id}` | Update a restaurant |
| GET | `/restaurants/{restaurant_id}/menu` | A restaurant's menu; `404` if the restaurant is unknown or has no menu |
| GET | `/restaurants/{restaurant_id}/menu/items` | The items on a restaurant's menu; same `404`s as above |
| POST | `/restaurants/{restaurant_id}/menu/items` | Add a menu item |
| PATCH | `/restaurants/{restaurant_id}/menu/items/{item_id}` | Update a menu item |
| GET | `/cart` | Get the signed-in customer's cart |
| POST | `/cart/items` | Add a menu item to the cart |
| PATCH | `/cart/items/{item_id}` | Change a cart item's quantity |
| DELETE | `/cart/items/{item_id}` or `/cart` | Remove an item or clear the cart |
| GET | `/orders` | The logged-in customer's orders; `401` without a token |
| GET | `/orders/{order_id}` | One order; only its customer or an admin (`403` otherwise), `404` if unknown |
| POST | `/checkout` | Turn your cart into an order at current prices, then empty the cart; `409` if the cart is empty or an item is unavailable (nothing saved) |
| PATCH | `/orders/{order_id}/status` | Owner of the order's restaurant or admin moves it on: body `{"status": "accepted" \| "preparing" \| "ready" \| "cancelled"}`; `409` if the lifecycle doesn't allow the move, `422` for any other status (out_for_delivery/delivered come from delivery) |
| POST | `/orders/{order_id}/cancel` | The customer who placed it, or an admin, cancels it while it is `placed` or `accepted`; `409` once preparation has started |
| GET | `/restaurants/{restaurant_id}/orders` | Every order placed at a restaurant, in any status; only its owner or an admin (`403` otherwise), `404` if the restaurant is unknown |

The customer front end supports registration and sign-in, profile management, browsing menus, adding and updating cart items, checkout, and viewing order history and details. The management front end can create and edit restaurants and menu items using these API endpoints.

## Demo management accounts

The committed JSON seed data includes two local/demo-only accounts so the management page can be demonstrated without manually editing the data files.

Both accounts use Argon2 password hashes in `data/customers.json`. The plaintext passwords below are provided only for local coursework demonstrations. Do not reuse these credentials or use them in a deployed environment.

| Role | Email (login username) | Demo password |
| --- | --- | --- |
| Admin | `admin@snackoverflow.demo` | `AdminDemo2026!` |
| Owner | `owner@snackoverflow.demo` | `OwnerDemo2026!` |

Open http://127.0.0.1:8000/management and sign in with either account.

- The admin can manage every seeded restaurant.
- The owner account (ID `2`) owns all three seeded restaurants and can manage their details and menu items.
- Newly registered accounts continue to receive the `customer` role and cannot perform owner/admin management actions.

The demo accounts are stored in the repository's seed JSON files. If you use a separate data directory through `SNACKOVERFLOW_DATA_DIR`, copy the seed files into that directory to make these accounts available.

## Data

Representative restaurant data is stored in `data/restaurants.json`.

The data folder can be changed with the `SNACKOVERFLOW_DATA_DIR` environment variable. Tests point the app at a temporary folder so the committed data is never modified.

### What an order keeps

An order records the transaction as it happened at checkout. Later menu, restaurant or profile changes don't rewrite it.

| Order field | Kind | Notes |
| --- | --- | --- |
| `lines[].name`, `lines[].unit_price`, `lines[].quantity`, `lines[].line_total`, `total` | Snapshot | Copied at checkout from the menu's current price |
| `restaurant_name` | Snapshot | The restaurant's name at checkout |
| `delivery_address` | Snapshot | The customer's address at checkout; the restaurant's owner sees it too, so the order can be delivered |
| `created_at` | Snapshot | When the order was placed |
| `status` | Current | Moves through the order lifecycle |
| `customer_id`, `restaurant_id`, `lines[].item_id` | Reference | Point at current records, used for access checks and reports; the order stays readable even if those records change or disappear |

Orders saved before `restaurant_name` and `delivery_address` existed load with those fields empty (`null`).

## Running tests

```bash
python -m pytest
```

## Repository structure

```text
app/
  main.py        FastAPI app, registers the routers
  routes/        HTTP endpoints (routes -> services)
  services/      business logic (services -> repositories)
  repositories/  reads and writes the JSON data files
  models/        Pydantic models (the API data contract)
  core/          configuration (data paths)
data/            representative JSON data
tests/           pytest test suite
docs/            project documentation, including PROVENANCE.md
scrum/           team agreement
requirements.txt
pytest.ini
```

## AI use

AI use is recorded in `docs/PROVENANCE.md`, following the course provenance guide.

## M2 Menu Availability and Cart

Menu items support `available` and `active` flags through the existing POST/PATCH endpoints. Customer browsing hides unavailable or inactive items.

Authenticated cart operations are documented in `/docs`:

| Method | Path | Operation |
| --- | --- | --- |
| GET | `/cart` | Get or create the current customer's active cart and backend totals |
| POST | `/cart/items` | Add an item using restaurant_id, item_id and quantity |
| PATCH | `/cart/items/{item_id}` | Replace quantity |
| DELETE | `/cart/items/{item_id}` | Remove an item |
| DELETE | `/cart` | Clear the cart |

The customer front end sends the bearer token received from `/auth/login`. A cart contains items from one restaurant; quantities are integers 1–99. Totals use current menu prices.

Design evidence: [shared menu orderability validation](docs/decision-receipt-menu-cart-M2.md).
