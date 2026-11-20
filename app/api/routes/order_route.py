from fastapi import APIRouter, Depends, HTTPException, status
from app.api import auth
from app.services.order_service import order_service_checkout, order_service_get_by_id, order_service_get_by_customer
from app.errors import CheckoutCustomerInactiveError, EmptyCartError, InvalidCartError, OrderNotFoundError
from app.schemas.account import AccountRead
from app.schemas.order import OrderRead
from app.services.account_service import get_account, require_owner

router = APIRouter()


# US1 Checkout: turn the customer's active cart into a saved order.
# Service errors are translated here: inactive customer -> 403, empty or invalid cart -> 400.
# The signed-in customer must be the owner of customer_id: no session -> 401, another customer -> 403.
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
        401: {"description": "Missing, invalid, or expired session"},
        403: {"description": "Customer account is deactivated, or customer_id belongs to another customer"},
    },
)
def order_route_checkout(customer_id: int, account: AccountRead = Depends(auth.customer)) -> OrderRead:
    require_owner(account, customer_id)
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


# US2 View one order: look up a saved order by its id.
# No session -> 401, order does not exist -> 404, order belongs to another customer -> 403.
@router.get(
    "/orders/{order_id}",
    status_code=status.HTTP_200_OK,
    summary="Get an order by id",
    description="Returns the order as saved at checkout, with the item names and prices at that time.",
    responses={
        401: {"description": "Missing, invalid, or expired session"},
        403: {"description": "The order belongs to another customer"},
        404: {"description": "Order not found"},
    },
)
def order_route_get_by_id(order_id: int, account: AccountRead = Depends(auth.customer)) -> OrderRead:
    try:
        order = order_service_get_by_id(order_id)
    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    require_owner(account, order.customer_id)
    return order


# US3 Order history: list all orders placed by one customer (empty list if none).
# No session -> 401, customer does not exist -> 404, another customer's history -> 403.
@router.get(
    "/customers/{customer_id}/orders",
    status_code=status.HTTP_200_OK,
    summary="List a customer's orders",
    description="Returns all orders placed by the customer, or an empty list if there are none.",
    responses={
        401: {"description": "Missing, invalid, or expired session"},
        403: {"description": "customer_id belongs to another customer"},
        404: {"description": "Customer not found"},
    },
)
def order_route_get_by_customer(customer_id: int, account: AccountRead = Depends(auth.customer)) -> list[OrderRead]:
    get_account(customer_id)
    require_owner(account, customer_id)
    return order_service_get_by_customer(customer_id)