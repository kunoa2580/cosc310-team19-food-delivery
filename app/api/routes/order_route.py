from fastapi import APIRouter, HTTPException, status
from app.services.order_service import order_service_checkout
from app.errors import CheckoutCustomerInactiveError, EmptyCartError, InvalidCartError
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