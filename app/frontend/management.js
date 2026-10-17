const restaurantSelect = document.querySelector("#restaurant-select");
const restaurantForm = document.querySelector("#restaurant-form");
const restaurantList = document.querySelector("#restaurant-list");
const restaurantStatus = document.querySelector("#restaurant-status");
const restaurantFormHeading = document.querySelector("#restaurant-form-heading");
const restaurantSubmit = document.querySelector("#restaurant-submit");
const restaurantFields = {
  name: document.querySelector("#restaurant-name"),
  cuisine: document.querySelector("#restaurant-cuisine"),
  address: document.querySelector("#restaurant-address"),
  rating: document.querySelector("#restaurant-rating"),
};
const menuSection = document.querySelector("#menu-management");
const menuRestaurantName = document.querySelector("#menu-restaurant-name");
const menuStatus = document.querySelector("#menu-status");
const menuList = document.querySelector("#menu-list");
const menuForm = document.querySelector("#menu-form");
const menuFormHeading = document.querySelector("#menu-form-heading");
const menuSubmit = document.querySelector("#menu-submit");
const menuCancelEdit = document.querySelector("#menu-cancel-edit");
const menuItemName = document.querySelector("#menu-item-name");
const menuItemPrice = document.querySelector("#menu-item-price");

let restaurants = [];
let menuItems = [];
let editingItemId = null;

function setStatus(element, message, isError = false) {
  element.textContent = message;
  element.classList.toggle("error", isError);
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const body = await response.json();
      if (body.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch (error) {
      // Keep the HTTP status as the useful error when the response has no JSON body.
    }
    const error = new Error(detail);
    error.status = response.status;
    throw error;
  }
  return response.json();
}

function selectedRestaurant() {
  const id = Number(restaurantSelect.value);
  return restaurants.find((restaurant) => restaurant.id === id);
}

function clearRestaurantFields() {
  Object.values(restaurantFields).forEach((field) => { field.value = ""; });
}

function renderRestaurants() {
  restaurantList.replaceChildren();
  restaurantSelect.replaceChildren(new Option("Create a new restaurant", ""));

  restaurants.forEach((restaurant) => {
    restaurantSelect.append(new Option(`${restaurant.name} (#${restaurant.id})`, restaurant.id));
    const row = document.createElement("li");
    row.append(
      document.createTextNode(
        `${restaurant.name} | ${restaurant.cuisine} | ${restaurant.address} | Rating: ${restaurant.rating.toFixed(1)} `,
      ),
    );
    const editButton = document.createElement("button");
    editButton.type = "button";
    editButton.textContent = "Edit restaurant and menu";
    editButton.addEventListener("click", () => {
      restaurantSelect.value = String(restaurant.id);
      selectRestaurant();
    });
    row.append(editButton);
    restaurantList.append(row);
  });

  if (!restaurants.length) {
    restaurantList.append(document.createTextNode("No restaurants available yet."));
  }
}

async function loadRestaurants(selectedId = "") {
  setStatus(restaurantStatus, "Loading restaurants...");
  try {
    restaurants = await requestJson("/restaurants");
    renderRestaurants();
    restaurantSelect.value = selectedId;
    setStatus(restaurantStatus, restaurants.length ? "" : "No restaurants available yet.");
    if (selectedId) await selectRestaurant();
  } catch (error) {
    setStatus(restaurantStatus, `Restaurants could not be loaded: ${error.message}`, true);
  }
}

async function loadMenu(restaurant) {
  menuItems = [];
  menuList.replaceChildren();
  setStatus(menuStatus, "Loading menu...");
  try {
    menuItems = await requestJson(`/restaurants/${restaurant.id}/menu/items`);
    renderMenu();
  } catch (error) {
    if (error.status === 404) {
      renderMenu();
      return;
    }
    setStatus(menuStatus, `Menu could not be loaded: ${error.message}`, true);
  }
}

function renderMenu() {
  menuList.replaceChildren();
  if (!menuItems.length) {
    setStatus(menuStatus, "No menu items yet. Add the first one below.");
    return;
  }

  setStatus(menuStatus, "");
  menuItems.forEach((item) => {
    const row = document.createElement("li");
    row.append(document.createTextNode(`${item.name} | $${item.price.toFixed(2)} `));
    const editButton = document.createElement("button");
    editButton.type = "button";
    editButton.textContent = "Edit item";
    editButton.addEventListener("click", () => {
      editingItemId = item.item_id;
      menuItemName.value = item.name;
      menuItemPrice.value = item.price;
      menuFormHeading.textContent = `Edit menu item #${item.item_id}`;
      menuSubmit.textContent = "Save menu item";
      menuCancelEdit.hidden = false;
      menuItemName.focus();
    });
    row.append(editButton);
    menuList.append(row);
  });
}

async function selectRestaurant() {
  const restaurant = selectedRestaurant();
  if (!restaurant) {
    restaurantFormHeading.textContent = "Create a restaurant";
    restaurantSubmit.textContent = "Create restaurant";
    clearRestaurantFields();
    menuSection.hidden = true;
    return;
  }

  restaurantFields.name.value = restaurant.name;
  restaurantFields.cuisine.value = restaurant.cuisine;
  restaurantFields.address.value = restaurant.address;
  restaurantFields.rating.value = restaurant.rating;
  restaurantFormHeading.textContent = `Edit restaurant #${restaurant.id}`;
  restaurantSubmit.textContent = "Save restaurant";
  menuSection.hidden = false;
  menuRestaurantName.textContent = restaurant.name;
  resetMenuForm();
  await loadMenu(restaurant);
}

function resetMenuForm() {
  editingItemId = null;
  menuForm.reset();
  menuFormHeading.textContent = "Add a menu item";
  menuSubmit.textContent = "Add menu item";
  menuCancelEdit.hidden = true;
}

restaurantSelect.addEventListener("change", selectRestaurant);

restaurantForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const restaurant = selectedRestaurant();
  const payload = {
    name: restaurantFields.name.value.trim(),
    cuisine: restaurantFields.cuisine.value.trim(),
    address: restaurantFields.address.value.trim(),
    rating: Number(restaurantFields.rating.value),
  };

  try {
    const saved = restaurant
      ? await requestJson(`/restaurants/${restaurant.id}`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        })
      : await requestJson("/restaurants", {
          method: "POST",
          body: JSON.stringify(payload),
        });
    await loadRestaurants(String(saved.id));
    setStatus(restaurantStatus, `Restaurant "${saved.name}" saved.`);
  } catch (error) {
    setStatus(restaurantStatus, `Restaurant could not be saved: ${error.message}`, true);
  }
});

menuForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const restaurant = selectedRestaurant();
  if (!restaurant) return;

  const payload = {
    name: menuItemName.value.trim(),
    price: Number(menuItemPrice.value),
  };
  const url = editingItemId === null
    ? `/restaurants/${restaurant.id}/menu/items`
    : `/restaurants/${restaurant.id}/menu/items/${editingItemId}`;

  try {
    await requestJson(url, {
      method: editingItemId === null ? "POST" : "PATCH",
      body: JSON.stringify(payload),
    });
    resetMenuForm();
    await loadMenu(restaurant);
    setStatus(menuStatus, "Menu item saved.");
  } catch (error) {
    setStatus(menuStatus, `Menu item could not be saved: ${error.message}`, true);
  }
});

menuCancelEdit.addEventListener("click", resetMenuForm);

loadRestaurants();
