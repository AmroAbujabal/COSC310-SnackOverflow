const restaurantGrid = document.querySelector("#restaurant-grid");
const statusMessage = document.querySelector("#status");
const searchInput = document.querySelector("#search-input");
const resultCount = document.querySelector("#result-count");
const menuPanel = document.querySelector("#menu-panel");

let allRestaurants = [];

function makeElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function setStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.classList.toggle("error", isError);
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
      document.createTextNode(` | Cuisine: ${restaurant.cuisine} | Address: ${restaurant.address} | Rating: ${restaurant.rating.toFixed(1)} `),
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
    const response = await fetch(`/restaurants/${restaurant.id}/menu/items`);
    if (!response.ok) throw new Error("Menu unavailable");
    const items = await response.json();
    const list = makeElement("ul", "menu-list");
    if (!items.length) {
      menuPanel.append(makeElement("p", "menu-empty", "This restaurant has no menu items listed yet."));
      return;
    }
    items.forEach((item) => {
      const row = makeElement("li", "menu-item");
      row.append(makeElement("span", "", item.name), makeElement("span", "menu-price", `$${item.price.toFixed(2)}`));
      list.append(row);
    });
    menuPanel.append(list);
  } catch (error) {
    menuPanel.append(makeElement("p", "menu-empty", "The menu is not available right now."));
  }
}

async function initialize() {
  try {
    const response = await fetch("/restaurants");
    if (!response.ok) throw new Error("Could not load restaurants.");
    allRestaurants = await response.json();
    renderRestaurants(allRestaurants);
    setStatus(allRestaurants.length ? "" : "No restaurants available yet.");
  } catch (error) {
    setStatus("Restaurants could not be loaded. Check that the API is running and try again.", true);
  }
}

searchInput.addEventListener("input", loadRestaurants);

initialize();