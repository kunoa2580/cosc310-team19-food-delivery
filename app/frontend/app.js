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
let localMenuEdits = false;

// Shared credentials for the demo customer. This account is separate from personal accounts.
const demoCustomer = { email: "customer@demo.com", password: "demo-customer-123" };

function element(id) {
    return document.getElementById(id);
}

function showNotice(message, isError = false) {
    const notice = element("notice");
    notice.textContent = message;
    notice.className = isError ? "notice error" : "notice";
    notice.hidden = !message;
}

function canManageRestaurants() {
    return account?.role === "restaurant" || account?.role === "admin";
}

function canEditMenu() {
    return localMenuEdits || canManageRestaurants();
}

function showView(id) {
    const isCustomer = account?.role === "customer";
    const canEditRestaurant = canManageRestaurants();
    const managementView = id === "manage-view" || id === "manage-restaurant-view";
    document.querySelectorAll(".view").forEach(function (view) {
        view.hidden = view.id !== id;
    });
    element("guest-sign-in").hidden = !!account || id === "login-view" || managementView;
    element("open-management").hidden = id === "login-view" || managementView;
    element("open-cart").hidden = !isCustomer || id === "cart-view";
    element("open-account").hidden = !isCustomer || id === "account-view";
    element("sign-out").hidden = !account;
    element("management-sign-in-hint").hidden = !managementView || canEditRestaurant || localMenuEdits;
    element("new-restaurant").hidden = !canEditRestaurant;
    element("restaurant-fields").disabled = !canEditRestaurant;
    element("restaurant-actions").hidden = !canEditRestaurant;
    element("new-menu-item").hidden = !canEditMenu();
    element("menu-editor").hidden = !canEditMenu();
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
    try {
        await action();
    } catch (error) {
        if (error.status === 401 && sessionToken) clearAccount();
        showNotice(error.message === "Failed to fetch" ? "Cannot reach the backend. Make sure Uvicorn is running." : error.message, true);
    } finally {
        busy = false;
        document.querySelectorAll("button").forEach(function (button) { button.disabled = false; });
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

function showManagement() {
    selectedRestaurant = null;
    const container = element("managed-restaurants");
    let action = "View restaurant and menu";
    if (canManageRestaurants()) action = "Edit restaurant and menu";
    else if (localMenuEdits) action = "Edit menu";
    container.replaceChildren();
    if (restaurants.length === 0) emptyMessage(container, "No restaurants yet.");
    restaurants.forEach(function (restaurant) {
        const card = actionButton("", function () { return selectRestaurant(restaurant.id); }, "card restaurant-card");
        card.append(
            textNode("strong", restaurant.name),
            textNode("span", restaurant.cuisine_type, "muted"),
            textNode("span", action)
        );
        container.appendChild(card);
    });
    showView("manage-view");
}

async function browseManagement() {
    const [config] = await Promise.all([api("/ui-config"), loadRestaurants()]);
    localMenuEdits = config.local_menu_edits;
    showManagement();
}

function newRestaurant() {
    selectedRestaurant = null;
    menuItems = [];
    element("delete-restaurant").hidden = true;
    element("restaurant-form-title").textContent = "Create a restaurant";
    element("save-restaurant").textContent = "Create restaurant";
    fillForm("restaurant-form", null);
    element("menu-workspace").hidden = true;
    resetMenuForm();
    showView("manage-restaurant-view");
}

function managementMenu(restaurantId) {
    return api("/restaurant/" + restaurantId + "/menu-items");
}

async function selectRestaurant(id) {
    const restaurant = await api("/restaurants/" + id);
    const items = await managementMenu(id);
    selectedRestaurant = restaurant;
    menuItems = items;
    element("delete-restaurant").hidden = false;
    element("restaurant-form-title").textContent = canManageRestaurants()
        ? "Edit " + restaurant.name
        : restaurant.name;
    element("save-restaurant").textContent = "Save restaurant changes";
    fillForm("restaurant-form", restaurant);
    element("menu-workspace").hidden = false;
    renderMenu("manager-menu", menuItems, canEditMenu());
    resetMenuForm();
    showView("manage-restaurant-view");
}

async function saveRestaurant() {
    const values = readForm("restaurant-form");
    const creating = selectedRestaurant === null;
    const changes = creating ? values : changedFields(values, selectedRestaurant);
    if (Object.keys(changes).length === 0) { showNotice("No restaurant changes to save."); return; }

    const path = creating ? "/restaurants" : "/restaurants/" + selectedRestaurant.id;
    const restaurant = await api(path, creating ? "POST" : "PATCH", changes);
    await loadRestaurants();
    await selectRestaurant(restaurant.id);
    showNotice(creating ? "Restaurant created. You can now add menu items." : "Restaurant changes saved.");
}

async function deleteRestaurant() {
    if (!selectedRestaurant) throw new Error("Select a restaurant first.");
    const restaurant = selectedRestaurant;
    if (!window.confirm('Delete "' + restaurant.name + '"? This cannot be undone.')) return;

    await api("/restaurants/" + restaurant.id, "DELETE");
    await loadRestaurants();
    showManagement();
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
    menuItems = await managementMenu(selectedRestaurant.id);
    renderMenu("manager-menu", menuItems, canEditMenu());
}

async function saveMenuItem() {
    if (!selectedRestaurant) throw new Error("Select or create a restaurant first.");
    const values = readForm("menu-form");
    const creating = editingMenuItem === null;
    const changes = creating ? values : changedFields(values, editingMenuItem);
    if (Object.keys(changes).length === 0) { showNotice("No menu changes to save."); return; }

    const path = "/restaurant/" + selectedRestaurant.id + "/menu-items";
    if (creating) await api(path + "/create", "POST", changes);
    else await api(path + "/update/" + editingMenuItem.item_id, "PATCH", changes);
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

function openLogin() {
    showView("login-view");
    element("account-login").elements.email.focus();
}

bindClick("browse-guest", browseRestaurants);
bindClick("manage-restaurants", browseManagement);
bindClick("open-management", browseManagement);
bindClick("guest-sign-in", function () {
    selectedRestaurant = null;
    openLogin();
});
bindClick("sign-in-to-edit", openLogin);
bindClick("open-account", function () { showView("account-view"); });
bindClick("back-from-account", browseRestaurants);
bindClick("open-order-history", showOrderHistory);
bindClick("back-from-order-history", function () { showView("account-view"); });
bindClick("refresh-restaurants", loadRestaurants);
bindClick("back-to-restaurants", browseRestaurants);
bindClick("new-restaurant", newRestaurant);
bindClick("delete-restaurant", deleteRestaurant);
bindClick("back-to-management", showManagement);
bindClick("back-from-management", function () {
    if (account) return browseRestaurants();
    openLogin();
});
bindClick("refresh-manager", browseManagement);
bindClick("new-menu-item", function () { resetMenuForm(); element("menu-form").scrollIntoView({ behavior: "smooth" }); });
bindClick("cancel-menu-edit", resetMenuForm);
bindClick("open-cart", async function () { await loadCart(); showView("cart-view"); });
bindClick("refresh-cart", loadCart);
bindClick("back-from-cart", browseRestaurants);
bindClick("clear-cart", clearCart);
bindClick("checkout", checkout);
element("search").addEventListener("input", renderRestaurants);
element("cuisine").addEventListener("change", renderRestaurants);
element("availability").addEventListener("change", renderRestaurants);
element("restaurant-form").addEventListener("submit", function (event) { event.preventDefault(); run(saveRestaurant); });
element("menu-form").addEventListener("submit", function (event) { event.preventDefault(); run(saveMenuItem); });

function displayAccount(value) {
    if (account?.id !== value?.id) element("order-history-list").replaceChildren();
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
    await showSignedInAccount(await api("/auth/login", "POST", credentials));
}

async function showSignedInAccount(result) {
    sessionToken = result.access_token;
    displayAccount(result.account);
    element("account-login").reset();
    if (canManageRestaurants()) {
        const restaurantId = selectedRestaurant?.id;
        element("managed-restaurants").replaceChildren();
        showView("manage-view");
        await browseManagement();
        if (restaurantId) await selectRestaurant(restaurantId);
    } else {
        selectedRestaurant = null;
        showView("browse-view");
        await loadRestaurants();
    }
}

element("account-login").addEventListener("submit", function (event) {
    event.preventDefault();
    const credentials = Object.fromEntries(new FormData(event.target));
    run(function () { return signIn(credentials); });
});

bindClick("demo-sign-in", async function () {
    let result;
    try {
        result = await api("/auth/login", "POST", demoCustomer);
    } catch (error) {
        if (error.status !== 401) throw error;
        try {
            await api("/customers", "POST", { name: "Demo Customer", ...demoCustomer });
        } catch (registrationError) {
            // Another demo visitor may have registered the shared account first.
            if (registrationError.status !== 409) throw registrationError;
        }
        result = await api("/auth/login", "POST", demoCustomer);
    }
    await showSignedInAccount(result);
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
    menuItems = [];
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
        if (!line.availability) card.appendChild(availableTag(false));
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

function renderOrderItems(order) {
    const items = document.createElement("ul");
    order.items.forEach(function (item) {
        items.appendChild(textNode("li", item.quantity + " × " + item.name +
            " at $" + item.unit_price.toFixed(2) + " each"));
    });
    return items;
}

function renderOrder(order) {
    const confirmation = element("order-confirmation");
    confirmation.replaceChildren();
    confirmation.hidden = !order;
    if (!order) return;

    confirmation.append(
        textNode("h2", "Order #" + order.order_id + " placed"),
        renderOrderItems(order),
        textNode("p", "Final total $" + order.total.toFixed(2) + " CAD", "price")
    );
}

async function showOrderHistory() {
    const orders = await api("/customers/" + account.id + "/orders");
    const list = element("order-history-list");
    list.replaceChildren();
    if (orders.length === 0) emptyMessage(list, "You have no orders yet.");

    for (const order of orders) {
        const card = textNode("article", "", "panel");
        const placedAt = textNode("time", new Date(order.created_at).toLocaleString(), "muted");
        placedAt.dateTime = order.created_at;
        card.append(
            textNode("h2", "Order #" + order.order_id),
            placedAt,
            renderOrderItems(order),
            textNode("p", "Total $" + order.total.toFixed(2) + " CAD", "price")
        );
        list.appendChild(card);
    }
    showView("order-history-view");
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
