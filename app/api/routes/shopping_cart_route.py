from fastapi import APIRouter, HTTPException, status, exceptions,Path
import app
import random
from pydantic import BaseModel, Field, ValidationError
from typing import Protocol
from app.repositories.shopping_cart_repository import ShoppingCartRepository
from app.services.shopping_cart_service import shopping_cart_service
from fastapi import Depends
from app.api.auth import customer
from app.schemas.account import AccountRead

service = shopping_cart_service(ShoppingCartRepository())


# import app.services.customer_service as customer_service # assume customer service exists and has a method to get customer by ID
# import app.auth as auth # assume auth module exists for authentication and authorization
import app.services.menu_item_service as menu_item_service
from app.schemas.shopping_cart import (
    ItemInCartCreate, 
    ItemInCartRead, 
    ShoppingCartCreate,
    ShoppingCartRead, 
    ShoppingCartUpdate)
from app.errors import (
    MenuItemNotFoundError, 
    DuplicateMenuItemError, 
    InvalidMenuItemUpdateError, 
    MenuItemRestaurantNotFoundError, 
    CartItemNotFoundError,
    CartNotFoundError,
    CartRestaurantMismatchError, 
    MenuItemIsNotAvailableError
)

router = APIRouter(tags=["Shopping Cart"], responses={
    401: {"description": "Missing, invalid, or expired session"},
    403: {"description": "Inactive account or wrong role"},
    404: {"description": "Account, cart item, or menu item not found"},
})





    
class shopping_cart_route:
    """ 
 

    ```
    add_item( customer_id:int, restaurant_id:int, item_id:int, quantity:int=1)
    ```

    add menu items

    ```
    edit_item( customer_id:int,  item_id:int, quantity:int=1)
    ```

    update item quantities;

    ```
    remove_item( customer_id:int, item_id:int)
    ```

    remove menu items;

    ```
    clear_cart( customer_id:int)
    ```

    clear the cart;

    ```
    view_cart( customer_id:int)
    ```

    retrieve the active cart for a customer and retrieve current cart contents;

    ```
    total_cart_price( customer_id:int)
    ```

    retrieve authoritative subtotal and total values calculated by the backend. 


    """
    """  



    """
            
    @router.post("/cart/add/{restaurant_id}/{item_id}/{quantity}", status_code=status.HTTP_201_CREATED, response_model=ShoppingCartRead, summary="Add a menu item to the signed-in customer's cart")
    def add_item(restaurant_id: int, item_id: int, quantity: int = Path(gt=0), account: AccountRead = Depends(customer)) -> ShoppingCartRead:
        try:
            return service.cart_add_item_to_cart_service(
                account.id, restaurant_id, item_id, quantity
            )
        except CartRestaurantMismatchError as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
        except MenuItemNotFoundError as e:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
        except CartNotFoundError as e:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
        except MenuItemIsNotAvailableError as e:
            raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e))
        except MenuItemRestaurantNotFoundError as e:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
        except ValidationError as e:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(f"quantity entered equal or blow zero"))
    
    @router.patch("/cart/edit/{item_id}/{quantity}",status_code=status.HTTP_200_OK, response_model=ShoppingCartRead, summary="Change the quantity of an item in the cart")
    def edit_item(item_id: int, quantity: int = Path(gt=0),account: AccountRead = Depends(customer)) -> ShoppingCartRead:
        try:
            return service.cart_edit_item_to_cart_service(account.id, item_id, quantity)
        except CartItemNotFoundError as e:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
        
       

    @router.delete("/cart/remove/{item_id}", status_code=status.HTTP_200_OK, response_model=ShoppingCartRead, summary="Remove a single item from the cart")
    def remove_item( item_id:int,account: AccountRead = Depends(customer))  -> ShoppingCartRead:
        try:
            
            
            removed_item = service.cart_remove_item_from_cart_service(account.id, item_id)
            return removed_item
        except CartItemNotFoundError as e:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))

    @router.delete("/cart/clear/", status_code=status.HTTP_200_OK, response_model=ShoppingCartRead, summary="Remove every item from the cart")
    def clear_cart( account: AccountRead = Depends(customer))  -> ShoppingCartRead:
        try:
            
            cleared_cart = service.cart_empty_items_service(account.id)
            return cleared_cart
        except CartNotFoundError as e:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
        

    @router.get("/cart/view/", status_code=status.HTTP_200_OK, response_model=ShoppingCartRead, summary="Retrieve the signed-in customer's active cart")
    def view_cart(account: AccountRead = Depends(customer))  -> ShoppingCartRead:
        
        try:
           
            cart_items = service.cart_view_by_customer_service(account.id)
            return cart_items
        except CartNotFoundError as e:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))   

    @router.get("/cart/total", status_code=status.HTTP_200_OK, summary="Retrieve the backend calculated cart total for signed active customer")
    def total_cart_price( account: AccountRead = Depends(customer)) -> dict:
        try:
           
            total_price = service.total_cart_price_service(account.id)
        except CartNotFoundError as e:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
        return {"message": f"Total price for cart of user {account.id}", "total_price": total_price}
    