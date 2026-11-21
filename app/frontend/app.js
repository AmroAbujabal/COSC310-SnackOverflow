const restaurantGrid = document.querySelector("#restaurant-grid");
const statusMessage = document.querySelector("#status");
const searchInput = document.querySelector("#search-input");
const resultCount = document.querySelector("#result-count");
const menuPanel = document.querySelector("#menu-panel");
const accountStatus = document.querySelector("#account-status");
const authForms = document.querySelector("#auth-forms");
const signedInPanel = document.querySelector("#signed-in-panel");
const loginForm = document.querySelector("#login-form");
const registerForm = document.querySelector("#register-form");
const profileForm = document.querySelector("#profile-form");
const cartSection = document.querySelector("#cart-section");
const cartStatus = document.querySelector("#cart-status");
const cartItems = document.querySelector("#cart-items");
const cartTotal = document.querySelector("#cart-total");
const ordersSection = document.querySelector("#orders-section");
const ordersStatus = document.querySelector("#orders-status");
const ordersList = document.querySelector("#orders-list");
const orderDetail = document.querySelector("#order-detail");

const accessTokenKey = "snackoverflow_access_token";
let accessToken = sessionStorage.getItem(accessTokenKey);
let allRestaurants = [];
let currentCart = null;

function makeElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function setStatus(element, message, isError = false) {
  element.textContent = message;
  element.className = isError ? "error" : "";
}

async function requestJson(url, options = {}) {
  const headers = new Headers(options.headers || {});
  if (options.body && !(options.body instanceof URLSearchParams)) {
    headers.set("Content-Type", "application/json");
  }
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);

  const response = await fetch(url, { ...options, headers });
  if (response.status === 204) {
    if (!response.ok) throw new Error(`Request failed (${response.status}).`);
    return null;
  }

  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = body?.detail;
    throw new Error(
      typeof detail === "string"
        ? detail
        : detail
          ? JSON.stringify(detail)
          : `${response.status} ${response.statusText}`,
    );
  }
  return body;
}

function updateAuthVisibility(customer) {
  authForms.hidden = Boolean(customer);
  signedInPanel.hidden = !customer;
  cartSection.hidden = !customer;
  ordersSection.hidden = !customer;
  if (customer) {
    profileForm.elements.name.value = customer.name;
    profileForm.elements.email.value = customer.email;
    profileForm.elements.address.value = customer.address;
    setStatus(accountStatus, `Signed in as ${customer.name} (${customer.role}).`);
  } else {
    setStatus(accountStatus, "Browse restaurants or sign in to order.");
  }
}

async function loadProfile() {
  const customer = await requestJson("/customers/me");
  updateAuthVisibility(customer);
  return customer;
}

function clearSession() {
  accessToken = null;
  sessionStorage.removeItem(accessTokenKey);
  currentCart = null;
  updateAuthVisibility(null);
  cartItems.replaceChildren();
  cartTotal.textContent = "";
  ordersList.replaceChildren();
  orderDetail.hidden = true;
}

function renderRestaurants(restaurants) {
  restaurantGrid.replaceChildren();
  resultCount.textContent = `(${restaurants.length})`;

  if (!restaurants.length) {
    restaurantGrid.append(makeElement("li", "", "No restaurants match that search."));
    return;
  }

  restaurants.forEach((restaurant) => {
    const row = makeElement("li");
    row.append(
      makeElement("strong", "", restaurant.name),
      document.createTextNode(
        ` | Cuisine: ${restaurant.cuisine} | Address: ${restaurant.address} | Rating: ${restaurant.rating.toFixed(1)} `,
      ),
    );
    const menuButton = makeElement("button", "", "View menu");
    menuButton.type = "button";
    menuButton.addEventListener("click", () => showMenu(restaurant));
    row.append(menuButton);
    restaurantGrid.append(row);
  });
}

function loadRestaurants() {
  menuPanel.hidden = true;
  const query = searchInput.value.trim().toLowerCase();
  const matches = allRestaurants.filter((restaurant) =>
    [restaurant.name, restaurant.cuisine, restaurant.address, restaurant.rating.toFixed(1)]
      .some((value) => value.toLowerCase().includes(query)),
  );
  renderRestaurants(matches);
  setStatus(matches.length ? "" : "No restaurant information matches that search.");
}

function addMenuItemRow(item, restaurant) {
  const row = makeElement("li", "menu-item");
  row.append(
    makeElement("span", "", item.name),
    makeElement("span", "menu-price", `$${item.price.toFixed(2)}`),
  );
  const quantity = makeElement("input");
  quantity.type = "number";
  quantity.min = "1";
  quantity.max = "99";
  quantity.step = "1";
  quantity.value = "1";
  quantity.setAttribute("aria-label", `Quantity of ${item.name}`);
  const addButton = makeElement("button", "", "Add to cart");
  addButton.type = "button";
  addButton.addEventListener("click", async () => {
    if (!accessToken) {
      setStatus(accountStatus, "Sign in or create an account before adding items to your cart.", true);
      return;
    }
    if (!quantity.reportValidity()) return;

    addButton.disabled = true;
    try {
      currentCart = await requestJson("/cart/items", {
        method: "POST",
        body: JSON.stringify({
          restaurant_id: restaurant.id,
          item_id: item.item_id,
          quantity: Number(quantity.value),
        }),
      });
      renderCart(currentCart);
      setStatus(cartStatus, `${item.name} added to your cart.`);
    } catch (error) {
      setStatus(cartStatus, `Could not add item: ${error.message}`, true);
    } finally {
      addButton.disabled = false;
    }
  });
  row.append(quantity, addButton);
  return row;
}

async function showMenu(restaurant) {
  menuPanel.hidden = false;
  menuPanel.replaceChildren();
  const heading = makeElement("div", "menu-heading");
  const titleGroup = makeElement("div");
  titleGroup.append(makeElement("p", "eyebrow", "ON THE MENU"), makeElement("h3", "", restaurant.name));
  const closeButton = makeElement("button", "close-menu", "Close menu");
  closeButton.type = "button";
  closeButton.addEventListener("click", () => { menuPanel.hidden = true; });
  heading.append(titleGroup, closeButton);
  menuPanel.append(heading);
  menuPanel.scrollIntoView();

  try {
    const items = await requestJson(`/restaurants/${restaurant.id}/menu/items`);
    if (!items.length) {
      menuPanel.append(makeElement("p", "menu-empty", "This restaurant has no menu items listed yet."));
      return;
    }
    const orderableItems = items.filter((item) => item.available && item.active);
    if (!orderableItems.length) {
      menuPanel.append(makeElement("p", "menu-empty", "No items are available right now."));
      return;
    }
    const list = makeElement("ul", "menu-list");
    orderableItems.forEach((item) => list.append(addMenuItemRow(item, restaurant)));
    menuPanel.append(list);
  } catch (error) {
    menuPanel.append(makeElement("p", "menu-empty", `The menu could not be loaded: ${error.message}`));
  }
}

function renderCart(cart) {
  currentCart = cart;
  cartItems.replaceChildren();
  cartTotal.textContent = `Total: $${cart.total.toFixed(2)}`;

  if (!cart.items.length) {
    cartItems.append(makeElement("li", "", "Your cart is empty."));
  }

  cart.items.forEach((item) => {
    const row = makeElement("li");
    row.append(
      makeElement("span", "", `${item.name} — $${item.unit_price.toFixed(2)} each; line total $${item.line_total.toFixed(2)} `),
    );
    if (!item.orderable) {
      row.append(makeElement("strong", "", "Currently unavailable; remove this item before checkout. "));
    }
    const quantity = makeElement("input");
    quantity.type = "number";
    quantity.min = "1";
    quantity.max = "99";
    quantity.step = "1";
    quantity.value = String(item.quantity);
    quantity.setAttribute("aria-label", `Quantity of ${item.name} in cart`);
    const updateButton = makeElement("button", "", "Update quantity");
    updateButton.type = "button";
    updateButton.addEventListener("click", async () => {
      if (!quantity.reportValidity()) return;
      updateButton.disabled = true;
      try {
        const updated = await requestJson(`/cart/items/${item.item_id}`, {
          method: "PATCH",
          body: JSON.stringify({ quantity: Number(quantity.value) }),
        });
        renderCart(updated);
        setStatus(cartStatus, "Cart quantity updated.");
      } catch (error) {
        setStatus(cartStatus, `Could not update cart: ${error.message}`, true);
      } finally {
        updateButton.disabled = false;
      }
    });
    const removeButton = makeElement("button", "", "Remove");
    removeButton.type = "button";
    removeButton.addEventListener("click", async () => {
      removeButton.disabled = true;
      try {
        await requestJson(`/cart/items/${item.item_id}`, { method: "DELETE" });
        renderCart(await requestJson("/cart"));
        setStatus(cartStatus, `${item.name} removed from your cart.`);
      } catch (error) {
        setStatus(cartStatus, `Could not remove item: ${error.message}`, true);
        removeButton.disabled = false;
      }
    });
    row.append(quantity, updateButton, removeButton);
    cartItems.append(row);
  });
}

function renderOrders(orders) {
  ordersList.replaceChildren();
  if (!orders.length) {
    ordersList.append(makeElement("li", "", "You have not placed any orders yet."));
    return;
  }
  orders.forEach((order) => {
    const row = makeElement("li");
    row.append(document.createTextNode(
      `Order #${order.id} — ${new Date(order.created_at).toLocaleString()} — $${order.total.toFixed(2)} `,
    ));
    const viewButton = makeElement("button", "", "View order");
    viewButton.type = "button";
    viewButton.addEventListener("click", () => showOrder(order.id));
    row.append(viewButton);
    ordersList.append(row);
  });
}

function renderOrderDetail(order) {
  orderDetail.replaceChildren();
  orderDetail.hidden = false;
  orderDetail.append(makeElement("h3", "", `Order #${order.id}`));
  const lines = makeElement("ul");
  order.lines.forEach((line) => {
    lines.append(makeElement(
      "li",
      "",
      `${line.quantity} × ${line.name} at $${line.unit_price.toFixed(2)} — $${line.line_total.toFixed(2)}`,
    ));
  });
  orderDetail.append(
    lines,
    makeElement("p", "", `Status: ${order.status} | Total: $${order.total.toFixed(2)}`),
  );
}

async function loadAccountData() {
  const [cart, orders] = await Promise.all([
    requestJson("/cart"),
    requestJson("/orders"),
  ]);
  renderCart(cart);
  renderOrders(orders);
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new URLSearchParams();
  formData.set("username", loginForm.elements.email.value.trim());
  formData.set("password", loginForm.elements.password.value);
  const submitButton = loginForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  setStatus(accountStatus, "Signing in...");

  try {
    const response = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(typeof data.detail === "string" ? data.detail : "Sign-in failed.");
    }
    accessToken = data.access_token;
    sessionStorage.setItem(accessTokenKey, accessToken);
    loginForm.reset();
    await loadProfile();
    await loadAccountData();
  } catch (error) {
    clearSession();
    setStatus(accountStatus, `Sign-in failed: ${error.message}`, true);
  } finally {
    submitButton.disabled = false;
  }
});

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitButton = registerForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  setStatus(accountStatus, "Creating your account...");

  try {
    const customer = await requestJson("/auth/register", {
      method: "POST",
      body: JSON.stringify({
        name: registerForm.elements.name.value,
        email: registerForm.elements.email.value,
        password: registerForm.elements.password.value,
        address: registerForm.elements.address.value,
      }),
    });
    registerForm.reset();
    setStatus(accountStatus, `Account created for ${customer.email}. Sign in to start ordering.`);
  } catch (error) {
    setStatus(accountStatus, `Could not create account: ${error.message}`, true);
  } finally {
    submitButton.disabled = false;
  }
});

profileForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitButton = profileForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  try {
    const customer = await requestJson("/customers/me", {
      method: "PATCH",
      body: JSON.stringify({
        name: profileForm.elements.name.value,
        email: profileForm.elements.email.value,
        address: profileForm.elements.address.value,
      }),
    });
    updateAuthVisibility(customer);
    setStatus(accountStatus, "Profile updated.");
  } catch (error) {
    setStatus(accountStatus, `Could not update profile: ${error.message}`, true);
  } finally {
    submitButton.disabled = false;
  }
});

document.querySelector("#logout-button").addEventListener("click", () => {
  clearSession();
  setStatus(accountStatus, "You have signed out.");
});

document.querySelector("#deactivate-button").addEventListener("click", async () => {
  if (!window.confirm("Deactivate your account? You will be signed out and will no longer be able to order.")) {
    return;
  }
  try {
    await requestJson("/customers/me", { method: "DELETE" });
    clearSession();
    setStatus(accountStatus, "Your account has been deactivated.");
  } catch (error) {
    setStatus(accountStatus, `Could not deactivate account: ${error.message}`, true);
  }
});

document.querySelector("#checkout-button").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  button.disabled = true;
  setStatus(cartStatus, "Placing your order...");
  try {
    const order = await requestJson("/checkout", { method: "POST" });
    renderCart(await requestJson("/cart"));
    renderOrderDetail(order);
    renderOrders(await requestJson("/orders"));
    setStatus(cartStatus, `Order #${order.id} placed successfully.`);
    orderDetail.scrollIntoView();
  } catch (error) {
    setStatus(cartStatus, `Could not place order: ${error.message}`, true);
  } finally {
    button.disabled = false;
  }
});

document.querySelector("#clear-cart-button").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  button.disabled = true;
  try {
    await requestJson("/cart", { method: "DELETE" });
    renderCart(await requestJson("/cart"));
    setStatus(cartStatus, "Cart cleared.");
  } catch (error) {
    setStatus(cartStatus, `Could not clear cart: ${error.message}`, true);
  } finally {
    button.disabled = false;
  }
});

async function showOrder(orderId) {
  orderDetail.hidden = false;
  setStatus(ordersStatus, `Loading order #${orderId}...`);
  try {
    renderOrderDetail(await requestJson(`/orders/${orderId}`));
    setStatus(ordersStatus, "");
  } catch (error) {
    setStatus(ordersStatus, `Could not load order: ${error.message}`, true);
  }
}

async function initialize() {
  try {
    const response = await fetch("/restaurants");
    if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
    allRestaurants = await response.json();
    renderRestaurants(allRestaurants);
    setStatus(allRestaurants.length ? "" : "No restaurants available yet.");
  } catch (error) {
    setStatus(statusMessage, `Restaurants could not be loaded: ${error.message}`, true);
  }

  if (!accessToken) return;
  try {
    await loadProfile();
    await loadAccountData();
  } catch (error) {
    clearSession();
    setStatus(accountStatus, `Your saved sign-in is no longer valid: ${error.message}`, true);
  }
}

searchInput.addEventListener("input", loadRestaurants);
initialize();
