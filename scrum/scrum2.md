Kenneth Customers + Auth (he built the createupdate and persistence code in M1)

Build

modelscustomer.py, repositoriescustomer_repository.py, datacustomers.json
Register, get, update details and address, and deactivate a customer.
Sign in with hashed passwords and a token.
A get_current_user dependency and a require_role(...) check, returning 401403 for bad requests.
Restrict restaurant and menu createupdate to owneradmin roles.

Improvement a shared JsonRepository base class that removes the duplicated loadsavenext-ID code. He wrote both copies, so this is a natural fit. Also update conftest.py to write every data file to the temp folder.

Get done first merge a minimal get_current_user early, because everyone else depends on it.

Al-Munther Menu availability + Cart (he built the menu code in M1)

Build

Add available bool = True to MenuItem, plus a way to deactivate an item.
Hide unavailable items from the customer menu.
modelscart.py, repositoriescart_repository.py, servicescart_service.py, routescart.py, datacarts.json.
Cart operations get or create the active cart, add an item, change a quantity, remove an item, clear the cart, and calculate totals on the backend.
Rules
one active cart per customer
items from one restaurant per cart
no unavailable, deactivated or nonexistent items
quantities must be valid
a deactivated customer gets blocked

Improvement one MenuService.get_orderable_item() that both the cart and checkout call, so the “is this item valid” check lives in one place. Also make get_menu raise an error instead of returning None.

Get done first the available flag, since checkout needs it to recheck items.

Amr Checkout + Orders + integration (you built restaurants and did the end-to-end check in M1)

Build

modelsorder.py, repositoriesorder_repository.py, servicescheckout_service.py, routesorders.py, dataorders.json.
POST checkout, which
rechecks the customer, cart, item availability and prices
recalculates the total
saves the order
clears the cart only after the save succeeds
GET orders{id} and GET customers{id}orders. Store item names and prices on the order itself, so the order history stays accurate if the menu changes later.
The integration test that walks Customer → Menu → Cart → Checkout → Order.
The restart persistence check.

Improvement a base DomainError class with subclasses (NotFoundError, BusinessRuleError, ForbiddenError) and one handler in main.py that turns them into HTTP responses. Then replace the HTTPException calls in menus.py. Do this early so Kenneth and Al-Munther raise the same exceptions.

Manveer (Cucumber1273) Frontend + docs + submission (same role as M1)

Build

Register and log-in screens.
Store the token and send it with every request.
Cart page with add, change-quantity and remove, showing the total from the backend.
Checkout button and an order confirmation or history view.
Send the token from the management page too, so restricted actions work after auth lands.
Docs README, docsmilestonesM2.md, docsPROVENANCE.md, and Team Receipt M2.3 (he collects everyone’s improvement and links to their PRs and tests).
Release the m2-integrated-system tag, the commit SHA, and the Canvas submission.

Improvement one shared api.js client (base URL, auth header, error handling) to replace the separate fetch code in app.js and management.js.

Order and shared files
Week 1
Amr the error classes.
Kenneth the auth dependency and the base repo.
Al-Munther the available flag.
These are small PRs, and everything else builds on them.
Weeks 2–3
Kenneth customers.
Al-Munther cart.
Amr checkout and orders.
Manveer frontend pages against the merged endpoints.
Week 4 the integration test passes, everyone runs through the demo scenarios, then tag and submit.

Everyone will touch coreconfig.py (add your data file), main.py (register your router) and conftest.py, so keep those edits small to avoid merge conflicts. Each owner writes the
