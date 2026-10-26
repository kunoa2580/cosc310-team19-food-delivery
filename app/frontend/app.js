// Restaurant paths are plural; the registered menu router uses singular /restaurant.
// Every write goes to FastAPI, which saves data through services and repositories.
let role = null;
let restaurants = [];
let selectedRestaurant = null;
let menuItems = [];
let editingMenuItem = null;
let busy = false;

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
    document.querySelectorAll(".view").forEach(function (view) {
        view.hidden = view.id !== id;
    });
    element("logout").hidden = role === null;
    element("role-label").textContent = role === null ? "" : role === "customer" ? "Customer view" : "Restaurant view";
}

// Handles FastAPI string errors, Pydantic's error list, and empty DELETE responses.
async function api(path, method = "GET", body = null) {
    const options = { method: method };
    if (body !== null) {
        options.headers = { "Content-Type": "application/json" };
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
        throw new Error(typeof detail === "string" ? detail : "Request failed (HTTP " + response.status + ").");
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

async function enterRole(selectedRole) {
    await loadRestaurants();
    role = selectedRole;
    if (role === "restaurant") { newRestaurant(); showView("manage-view"); }
    else showView("browse-view");
}

function bindClick(id, action) {
    element(id).addEventListener("click", function () { run(action); });
}

bindClick("customer-login", function () { return enterRole("customer"); });
bindClick("restaurant-login", function () { return enterRole("restaurant"); });
bindClick("logout", function () {
    role = null;
    selectedRestaurant = null;
    editingMenuItem = null;
    showView("login-view");
});
bindClick("refresh-restaurants", loadRestaurants);
bindClick("back-to-restaurants", async function () { await loadRestaurants(); showView("browse-view"); });
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
element("search").addEventListener("input", renderRestaurants);
element("cuisine").addEventListener("change", renderRestaurants);
element("availability").addEventListener("change", renderRestaurants);
element("managed-restaurant").addEventListener("change", function () {
    run(function () { return selectRestaurant(element("managed-restaurant").value); });
});
element("restaurant-form").addEventListener("submit", function (event) { event.preventDefault(); run(saveRestaurant); });
element("menu-form").addEventListener("submit", function (event) { event.preventDefault(); run(saveMenuItem); });
showView("login-view");
