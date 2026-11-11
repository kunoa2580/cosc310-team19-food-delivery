from fastapi import APIRouter, HTTPException, status
from app.services.order_service import order_service_checkout, order_service_get_by_id
from app.errors import CheckoutCustomerInactiveError, EmptyCartError, InvalidCartError, OrderNotFoundError
from app.schemas.order import OrderRead

router = APIRouter()


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