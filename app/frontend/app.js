// Restaurant paths are plural; the registered menu router uses singular /restaurant.
// Every write goes to FastAPI, which saves data through services and repositories.
let restaurants = [];
let selectedRestaurant = null;
let menuItems = [];
let editingMenuItem = null;
let busy = false;
let account = null;
let sessionToken = "";
let cart = null;
let viewedRestaurantId = null;

function element(id) {
    return document.getElementById(id);
}

function showNotice(message, isError = false) {
    const notice = element("notice");
    notice.textContent = message;
    notice.className = isError ? "notice error" : "notice";
    notice.hidden = !message;
}

function showView(id) {
    const isCustomer = account?.role === "customer";
    document.querySelectorAll(".view").forEach(function (view) {
        view.hidden = view.id !== id;
    });
    element("guest-sign-in").hidden = !!account || id === "login-view";
    element("open-cart").hidden = !isCustomer || id === "cart-view";
    element("open-account").hidden = !isCustomer || id === "account-view";
    element("sign-out").hidden = !account;
}

// Handles FastAPI string errors, Pydantic's error list, and empty DELETE responses.
async function api(path, method = "GET", body = null) {
    const options = { method: method, headers: {} };
    if (sessionToken) options.headers["Authorization"] = "Bearer " + sessionToken;
    if (body !== null) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(body);
    }
    const response = await fetch(path, options);
    if (response.status === 204) return null;
    const text = await response.text();
    let data;
    try {
        data = text ? JSON.parse(text) : null;
    } catch (error) {
        throw new Error("The server returned an unexpected response (HTTP " + response.status + "). Check the terminal.");
    }
    if (!response.ok) {
        let detail = data && data.detail;
        if (Array.isArray(detail)) {
            detail = detail.map(function (error) {
                return error.loc.join(".") + ": " + error.msg;
            }).join("\n");
        }
        const failure = new Error(typeof detail === "string" ? detail : "Request failed (HTTP " + response.status + ").");
        failure.status = response.status;
        throw failure;
    }
    return data;
}

// Prevent a second action while the first request is still running.
async function run(action) {
    if (busy) return;
    busy = true;
    showNotice("");
    const buttons = document.querySelectorAll("button");
    buttons.forEach(function (button) { button.disabled = true; });
    element("managed-restaurant").disabled = true;
    try {
        await action();
    } catch (error) {
        if (error.status === 401 && sessionToken) clearAccount();
        showNotice(error.message === "Failed to fetch" ? "Cannot reach the backend. Make sure Uvicorn is running." : error.message, true);
    } finally {
        busy = false;
        document.querySelectorAll("button").forEach(function (button) { button.disabled = false; });
        element("managed-restaurant").disabled = false;
    }
}

// Use textContent for backend values so restaurant names cannot inject HTML.
function textNode(tag, text, className = "") {
    const node = document.createElement(tag);
    node.textContent = text;
    node.className = className;
    return node;
}

function actionButton(label, action, className = "") {
    const button = textNode("button", label, className);
    button.type = "button";
    button.addEventListener("click", function () { run(action); });
    return button;
}

function availableTag(available) {
    return textNode("span", available ? "Available" : "Unavailable", available ? "tag" : "tag closed");
}

function emptyMessage(container, message) {
    container.appendChild(textNode("p", message, "empty"));
}

async function loadRestaurants() {
    restaurants = await api("/restaurants");
    const previous = element("cuisine").value;
    const cuisineSelect = element("cuisine");
    cuisineSelect.replaceChildren(new Option("All cuisines", ""));
    const cuisines = [];
    restaurants.forEach(function (restaurant) {
        if (!cuisines.includes(restaurant.cuisine_type)) cuisines.push(restaurant.cuisine_type);
    });
    cuisines.sort().forEach(function (cuisine) { cuisineSelect.add(new Option(cuisine, cuisine)); });
    if (cuisines.includes(previous)) cuisineSelect.value = previous;
    const managerSelect = element("managed-restaurant");
    managerSelect.replaceChildren(new Option("Choose a restaurant", ""));
    restaurants.forEach(function (restaurant) { managerSelect.add(new Option(restaurant.name, String(restaurant.id))); });
    renderRestaurants();
}

function renderRestaurants() {
    const search = element("search").value.trim().toLowerCase();
    const cuisine = element("cuisine").value;
    const availableOnly = element("availability").value === "open";
    const matched = restaurants.filter(function (restaurant) {
        const text = restaurant.name + " " + restaurant.address + " " + restaurant.cuisine_type;
        return text.toLowerCase().includes(search)
            && (!cuisine || restaurant.cuisine_type === cuisine)
            && (!availableOnly || restaurant.availability);
    });
    const container = element("restaurant-list");
    container.replaceChildren();
    element("restaurant-count").textContent = matched.length + " restaurant(s)";
    if (matched.length === 0) emptyMessage(container, "No restaurants match your search.");
    matched.forEach(function (restaurant) {
        const card = textNode("article", "", "card");
        card.append(availableTag(restaurant.availability), textNode("h3", restaurant.name),
            textNode("p", restaurant.cuisine_type + " · Rating " + restaurant.rating),
            textNode("p", restaurant.address, "muted"),
            actionButton("View restaurant", function () { return openDetails(restaurant.id); }));
        container.appendChild(card);
    });
}

async function openDetails(id) {
    // Fetch current details and menu rather than relying on the list's cached data.
    viewedRestaurantId = id;
    const restaurant = await api("/restaurants/" + id);
    const items = await api("/restaurant/" + id + "/menu-items");
    const details = element("restaurant-details");
    details.replaceChildren(textNode("h1", restaurant.name), availableTag(restaurant.availability));
    const list = document.createElement("dl");
    const fields = [
        ["Cuisine", restaurant.cuisine_type], ["Address", restaurant.address],
        ["Phone", restaurant.phone_number], ["Email", restaurant.email],
        ["Website", restaurant.website], ["Opening hours", restaurant.opening_hours], ["Rating", restaurant.rating]
    ];
    fields.forEach(function (field) { list.append(textNode("dt", field[0]), textNode("dd", field[1])); });
    details.appendChild(list);
    renderMenu("customer-menu", items, false);
    showView("details-view");
}

function renderMenu(containerId, items, management) {
    const container = element(containerId);
    container.replaceChildren();
    if (items.length === 0) emptyMessage(container, "No menu items yet.");
    items.forEach(function (item) {
        const card = textNode("article", "", "card");
        card.append(availableTag(item.availability), textNode("h3", item.name),
            textNode("p", item.description, "muted"), textNode("p", "$" + item.price.toFixed(2) + " CAD", "price"));
        if (management) {
            const actions = textNode("div", "", "button-row");
            actions.append(actionButton("Edit", function () { editMenuItem(item); }, "secondary"),
                actionButton("Delete", function () { return deleteMenuItem(item); }, "danger"));
            card.appendChild(actions);
        }
        else if (account?.role === "customer" && item.availability) {
            card.appendChild(actionButton("Add to cart", function () { return addToCart(item); }));
        }
        container.appendChild(card);
    });
}

function fillForm(formId, values) {
    const form = element(formId);
    form.reset();
    if (!values) return;
    Object.keys(values).forEach(function (name) {
        const input = form.elements.namedItem(name);
        if (!input) return;
        if (input.type === "checkbox") input.checked = values[name];
        else input.value = values[name];
    });
}

function readForm(formId) {
    const values = {};
    const inputs = element(formId).querySelectorAll("input, textarea");
    inputs.forEach(function (input) {
        // FastAPI/Pydantic validates text and parses numeric fields.
        values[input.name] = input.type === "checkbox" ? input.checked : input.value;
    });
    return values;
}

function changedFields(values, original) {
    const changes = {};
    Object.keys(values).forEach(function (name) {
        // Form text is compared with numeric API values in their displayed form.
        const previous = typeof original[name] === "number" ? String(original[name]) : original[name];
        if (values[name] !== previous) changes[name] = values[name];
    });
    return changes;
}

function newRestaurant() {
    selectedRestaurant = null;
    menuItems = [];
    element("delete-restaurant").hidden = true;
    element("managed-restaurant").value = "";
    element("restaurant-form-title").textContent = "Create a restaurant";
    element("save-restaurant").textContent = "Create restaurant";
    fillForm("restaurant-form", null);
    element("menu-workspace").hidden = true;
    resetMenuForm();
}

async function selectRestaurant(id) {
    if (!id) { newRestaurant(); return; }
    const restaurant = await api("/restaurants/" + id);
    const items = await api("/restaurant/" + id + "/menu-items");
    selectedRestaurant = restaurant;
    menuItems = items;
    element("delete-restaurant").hidden = false;
    element("managed-restaurant").value = String(id);
    element("restaurant-form-title").textContent = "Edit " + restaurant.name;
    element("save-restaurant").textContent = "Save restaurant changes";
    fillForm("restaurant-form", restaurant);
    element("menu-workspace").hidden = false;
    renderMenu("manager-menu", menuItems, true);
    resetMenuForm();
}

async function saveRestaurant() {
    const values = readForm("restaurant-form");
    let restaurant;
    const creating = selectedRestaurant === null;
    if (creating) restaurant = await api("/restaurants", "POST", values);
    else {
        const changes = changedFields(values, selectedRestaurant);
        if (Object.keys(changes).length === 0) { showNotice("No restaurant changes to save."); return; }
        restaurant = await api("/restaurants/" + selectedRestaurant.id, "PATCH", changes);
    }
    await loadRestaurants();
    await selectRestaurant(restaurant.id);
    showNotice(creating ? "Restaurant created. You can now add menu items." : "Restaurant changes saved.");
}

async function deleteRestaurant() {
    if (!selectedRestaurant) throw new Error("Select a restaurant first.");
    const restaurant = selectedRestaurant;
    if (!window.confirm('Delete "' + restaurant.name + '"? This cannot be undone.')) return;

    // Check current items before deleting through the management interface.
    const items = await api("/restaurant/" + restaurant.id + "/menu-items");
    if (items.length > 0) {
        throw new Error("Delete all menu items from this restaurant before deleting the restaurant.");
    }

    await api("/restaurants/" + restaurant.id, "DELETE");
    newRestaurant();
    await loadRestaurants();
    showNotice("Restaurant deleted.");
}

function resetMenuForm() {
    editingMenuItem = null;
    fillForm("menu-form", null);
    element("menu-form-title").textContent = "Add a menu item";
    element("save-menu-item").textContent = "Add item";
}

function editMenuItem(item) {
    editingMenuItem = item;
    fillForm("menu-form", item);
    element("menu-form-title").textContent = "Edit " + item.name;
    element("save-menu-item").textContent = "Save item changes";
    element("menu-form").scrollIntoView({ behavior: "smooth", block: "center" });
}

async function refreshMenu() {
    menuItems = await api("/restaurant/" + selectedRestaurant.id + "/menu-items");
    renderMenu("manager-menu", menuItems, true);
}

async function saveMenuItem() {
    if (!selectedRestaurant) throw new Error("Select or create a restaurant first.");
    const values = readForm("menu-form");
    const path = "/restaurant/" + selectedRestaurant.id + "/menu-items";
    const creating = editingMenuItem === null;
    if (creating) await api(path + "/create", "POST", values);
    else {
        const changes = changedFields(values, editingMenuItem);
        if (Object.keys(changes).length === 0) { showNotice("No menu changes to save."); return; }
        await api(path + "/update/" + editingMenuItem.item_id, "PATCH", changes);
    }
    await refreshMenu();
    resetMenuForm();
    showNotice(creating ? "Menu item added." : "Menu item changes saved.");
}

async function deleteMenuItem(item) {
    if (!window.confirm('Delete "' + item.name + '" from this menu?')) return;
    await api("/restaurant/" + selectedRestaurant.id + "/menu-items/delete/" + item.item_id, "DELETE");
    await refreshMenu();
    if (editingMenuItem && editingMenuItem.item_id === item.item_id) resetMenuForm();
    showNotice("Menu item deleted.");
}

async function browseRestaurants() {
    await loadRestaurants();
    showView("browse-view");
}

function bindClick(id, action) {
    element(id).addEventListener("click", function () { run(action); });
}

bindClick("browse-guest", browseRestaurants);
bindClick("guest-sign-in", function () { showView("login-view"); });
bindClick("open-account", function () { showView("account-view"); });
bindClick("back-from-account", browseRestaurants);
bindClick("refresh-restaurants", loadRestaurants);
bindClick("back-to-restaurants", browseRestaurants);
bindClick("new-restaurant", newRestaurant);
bindClick("delete-restaurant", deleteRestaurant);
bindClick("refresh-manager", async function () {
    const id = selectedRestaurant ? selectedRestaurant.id : null;
    await loadRestaurants();
    if (id && restaurants.some(function (restaurant) { return restaurant.id === id; })) await selectRestaurant(id);
    else newRestaurant();
});
bindClick("new-menu-item", function () { resetMenuForm(); element("menu-form").scrollIntoView({ behavior: "smooth" }); });
bindClick("cancel-menu-edit", resetMenuForm);
bindClick("open-cart", async function () { await loadCart(); showView("cart-view"); });
bindClick("back-from-cart", browseRestaurants);
bindClick("clear-cart", clearCart);
bindClick("checkout", checkout);
element("search").addEventListener("input", renderRestaurants);
element("cuisine").addEventListener("change", renderRestaurants);
element("availability").addEventListener("change", renderRestaurants);
element("managed-restaurant").addEventListener("change", function () {
    run(function () { return selectRestaurant(element("managed-restaurant").value); });
});
element("restaurant-form").addEventListener("submit", function (event) { event.preventDefault(); run(saveRestaurant); });
element("menu-form").addEventListener("submit", function (event) { event.preventDefault(); run(saveMenuItem); });

function displayAccount(value) {
    account = value;
    element("account-summary").textContent = account ? account.name + " — " + account.email : "";
    element("profile-form").elements.name.value = account?.name || "";
    element("address-form").elements.delivery_address.value = account?.delivery_address || "";
}

element("account-register").addEventListener("submit", function (event) {
    event.preventDefault();
    run(async function () {
        const registration = Object.fromEntries(new FormData(event.target));
        await api("/customers", "POST", registration);
        event.target.reset();
        element("registration-panel").open = false;
        element("account-login").elements.email.value = registration.email;
        showNotice("Account created. Sign in above.");
    });
});

async function signIn(credentials) {
    const result = await api("/auth/login", "POST", credentials);
    sessionToken = result.access_token;
    displayAccount(result.account);
    element("account-login").reset();
    if (account.role === "restaurant") {
        newRestaurant();
        showView("manage-view");
    } else {
        showView("browse-view");
    }
    await loadRestaurants();
}

element("account-login").addEventListener("submit", function (event) {
    event.preventDefault();
    const credentials = Object.fromEntries(new FormData(event.target));
    run(function () { return signIn(credentials); });
});

bindClick("demo-sign-in", async function () {
    const credentials = {
        email: "demo-" + crypto.randomUUID() + "@example.com",
        password: crypto.randomUUID(),
    };
    await api("/customers", "POST", { name: "Demo Customer", ...credentials });
    await signIn(credentials);
});

element("profile-form").addEventListener("submit", function (event) {
    event.preventDefault();
    run(async function () {
        displayAccount(await api("/customers/me", "PATCH", Object.fromEntries(new FormData(event.target))));
        showNotice("Name saved.");
    });
});
element("address-form").addEventListener("submit", function (event) {
    event.preventDefault();
    run(async function () {
        displayAccount(await api("/customers/me/address", "PUT", Object.fromEntries(new FormData(event.target))));
        showNotice("Delivery address saved.");
    });
});

function clearAccount() {
    displayAccount(null);
    sessionToken = "";
    selectedRestaurant = null;
    editingMenuItem = null;
    viewedRestaurantId = null;
    cart = null;
    renderCart();
    renderOrder(null);
    showView("login-view");
}
bindClick("sign-out", async function () {
    await api("/auth/logout", "POST");
    clearAccount();
});
bindClick("deactivate-account", async function () {
    if (!window.confirm("Deactivate your account? You will no longer be able to sign in.")) return;
    await api("/customers/me", "DELETE");
    clearAccount();
    showNotice("Account deactivated.");
});
// Keep the token in memory: reloading the page requires signing in again.
showView("login-view");


async function loadCart() {
    try {
        cart = await api("/cart/view/");
    } catch (error) {
        if (error.status !== 404) throw error;
        cart = null;
    }
    renderCart();
}

function renderCart() {
    const container = element("cart-list");
    container.replaceChildren();
    const lines = cart ? cart.items : [];
    element("cart-actions").hidden = lines.length === 0;
    element("cart-total").textContent = cart
        ? "Subtotal $" + cart.subtotal.toFixed(2) + " · Total $" + cart.total.toFixed(2) + " CAD"
        : "";
    if (lines.length === 0) {
        emptyMessage(container, "Your cart is empty.");
        return;
    }
    lines.forEach(function (line) {
        const card = textNode("article", "", "card");
        card.append(
            textNode("h3", line.name),
            textNode("p", "$" + line.price.toFixed(2) + " CAD each", "muted"),
            textNode("p", "Quantity: " + line.quantity)
        );
        const actions = textNode("div", "", "button-row");
        actions.append(
            actionButton("-", function () { return changeQuantity(line, line.quantity - 1); }, "secondary"),
            actionButton("+", function () { return changeQuantity(line, line.quantity + 1); }, "secondary"),
            actionButton("Remove", function () { return removeFromCart(line); }, "danger")
        );
        card.appendChild(actions);
        container.appendChild(card);
    });
}

function renderOrder(order) {
    const confirmation = element("order-confirmation");
    confirmation.replaceChildren();
    confirmation.hidden = !order;
    if (!order) return;

    const items = document.createElement("ul");
    order.items.forEach(function (item) {
        items.appendChild(textNode("li", item.quantity + " × " + item.name +
            " at $" + item.unit_price.toFixed(2) + " each"));
    });
    confirmation.append(
        textNode("h2", "Order #" + order.order_id + " placed"),
        items,
        textNode("p", "Final total $" + order.total.toFixed(2) + " CAD", "price")
    );
}

async function addToCart(item) {
    const restaurantId = item.restaurant_id || viewedRestaurantId;
    cart = await api("/cart/add/" + restaurantId + "/" + item.item_id + "/1", "POST");
    renderOrder(null);
    showNotice(item.name + " added to your cart.");
}

async function changeQuantity(line, quantity) {
    if (quantity < 1) return removeFromCart(line);   // PATCH rejects 0 with 422
    cart = await api("/cart/edit/" + line.item_id + "/" + quantity, "PATCH");
    renderCart();
}

async function removeFromCart(line) {
    cart = await api("/cart/remove/" + line.item_id, "DELETE");
    renderCart();
    showNotice("Item removed.");
}

async function clearCart() {
    if (!window.confirm("Remove every item from your cart?")) return;
    cart = await api("/cart/clear/", "DELETE");
    renderCart();
    showNotice("Cart cleared.");
}

async function checkout() {
    if (!cart || cart.items.length === 0) throw new Error("Your cart is empty.");
    const order = await api("/customers/" + account.id + "/checkout", "POST");
    cart = null;
    renderCart();
    renderOrder(order);
    await loadCart();
}
