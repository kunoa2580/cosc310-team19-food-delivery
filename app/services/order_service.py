from datetime import datetime, timezone

from app.repositories.order_repository import OrderRepository
from app.schemas.order import CheckoutCart, OrderItemRead, OrderRead
from app.services.menu_item_service import menu_service_get_by_id
from app.services.restaurant_service import restaurant_service_get_by_id
from app.errors import (
    CheckoutCustomerInactiveError,
    EmptyCartError,
    InvalidCartError,
    MenuItemNotFoundError,
    OrderNotFoundError,
    RestaurantNotFoundError,
)

order_repo = OrderRepository()

def _customer_is_active(customer_id: int) -> bool:
    raise NotImplementedError("Customer service is not merged yet")


def _get_active_cart(customer_id: int) -> CheckoutCart:
    raise NotImplementedError("Cart service is not merged yet")


def _clear_cart(customer_id: int) -> None:
    raise NotImplementedError("Cart service is not merged yet")

# US1 Checkout: turn the customer's active cart into a saved order.
# 1. Validate the customer, cart, restaurant, menu items and quantities (nothing is written yet).
# 2. Read names and prices from the current menu, never from the cart, and compute the total.
# 3. Save the order, and only then clear the cart, so a failed save never loses the cart.
def order_service_checkout(customer_id: int) -> OrderRead:
    if not _customer_is_active(customer_id):
        raise CheckoutCustomerInactiveError(f"Customer {customer_id} is not active")

    cart = _get_active_cart(customer_id)
    if not cart.items:
        raise EmptyCartError("Cannot check out an empty cart")

    try:
        restaurant = restaurant_service_get_by_id(cart.restaurant_id)
    except RestaurantNotFoundError:
        raise InvalidCartError(f"Restaurant {cart.restaurant_id} no longer exists")
    if not restaurant.availability:
        raise InvalidCartError(f"Restaurant {cart.restaurant_id} is not available")

    lines = []
    for cart_item in cart.items:
        if cart_item.quantity <= 0:
            raise InvalidCartError(f"Invalid quantity for item {cart_item.item_id}")
        try:
            menu_item = menu_service_get_by_id(cart.restaurant_id, cart_item.item_id)
        except MenuItemNotFoundError:
            raise InvalidCartError(f"Item {cart_item.item_id} no longer exists")
        if not menu_item.availability:
            raise InvalidCartError(f"Item {cart_item.item_id} is not available")
        # Copy the name and price into the order so later menu changes do not alter it.
        lines.append(
            OrderItemRead(
                item_id=menu_item.item_id,
                name=menu_item.name,
                unit_price=menu_item.price,
                quantity=cart_item.quantity,
            )
        )

    total = round(sum(line.unit_price * line.quantity for line in lines), 2)
    record = order_repo.order_repo_create(
        {
            "customer_id": customer_id,
            "restaurant_id": cart.restaurant_id,
            "items": [line.model_dump() for line in lines],
            "total": total,
            "status": "placed",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    _clear_cart(customer_id)
    return OrderRead(**record)


# US2 View one order: return a saved order, or raise OrderNotFoundError if the id does not exist.
def order_service_get_by_id(order_id: int) -> OrderRead:
    record = order_repo.order_repo_get_by_id(order_id)
    if record is None:
        raise OrderNotFoundError(f"Order {order_id} was not found")
    return OrderRead(**record)


# US3 Order history: all orders of one customer. No orders is not an error, so it returns [].
def order_service_get_by_customer(customer_id: int) -> list[OrderRead]:
    records = order_repo.order_repo_list_by_customer(customer_id)
    return [OrderRead(**record) for record in records]