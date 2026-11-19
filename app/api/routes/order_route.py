from fastapi import APIRouter, HTTPException, status
from app.services.order_service import order_service_checkout, order_service_get_by_id, order_service_get_by_customer
from app.errors import CheckoutCustomerInactiveError, EmptyCartError, InvalidCartError, OrderNotFoundError
from app.schemas.order import OrderRead

router = APIRouter()


# US1 Checkout: turn the customer's active cart into a saved order.
# Service errors are translated here: inactive customer -> 403, empty or invalid cart -> 400.
# customer_id is a path parameter until the auth dependency (current user) is merged.
@router.post(
    "/customers/{customer_id}/checkout",
    status_code=status.HTTP_201_CREATED,
    summary="Check out the customer's active cart",
    description=(
        "Validates the customer, restaurant, cart and menu items, recalculates prices from the "
        "current menu, saves the order, and clears the cart only after the order is saved."
    ),
    responses={
        400: {"description": "Cart is empty, or its restaurant or an item is unavailable or invalid"},
        403: {"description": "Customer account is deactivated"},
    },
)
def order_route_checkout(customer_id: int) -> OrderRead:
    try:
        order = order_service_checkout(customer_id)
    except CheckoutCustomerInactiveError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except (EmptyCartError, InvalidCartError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return order


# US2 View one order: look up a saved order by its id (404 if it does not exist).
# Any caller can read any order until the auth dependency is merged;
# then restrict it to the order's owner.
@router.get(
    "/orders/{order_id}",
    status_code=status.HTTP_200_OK,
    summary="Get an order by id",
    description="Returns the order as saved at checkout, with the item names and prices at that time.",
    responses={404: {"description": "Order not found"}},
)
def order_route_get_by_id(order_id: int) -> OrderRead:
    try:
        order = order_service_get_by_id(order_id)
    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    return order


# US3 Order history: list all orders placed by one customer (empty list if none).
# Any caller can read any customer's orders until the auth dependency is merged,
# and an unknown customer returns an empty list until the customer service is merged.
@router.get(
    "/customers/{customer_id}/orders",
    status_code=status.HTTP_200_OK,
    summary="List a customer's orders",
    description="Returns all orders placed by the customer, or an empty list if there are none.",
)
def order_route_get_by_customer(customer_id: int) -> list[OrderRead]:
    return order_service_get_by_customer(customer_id)