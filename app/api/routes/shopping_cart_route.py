from fastapi import APIRouter, HTTPException, status, exceptions
import app
import random
from pydantic import BaseModel, Field, ValidationError

from app.services.shopping_cart_service import (

    shopping_cart_service,

)

# import app.services.customer_service as customer_service # assume customer service exists and has a method to get customer by ID
# import app.auth as auth # assume auth module exists for authentication and authorization
import app.services.menu_item_service as menu_item_service
from app.schemas.shopping_cart import ItemInCartCreate, ItemInCartRead, ShoppingCartCreate,ShoppingCartRead, ShoppingCartUpdate
router = APIRouter()
service = shopping_cart_service()

from app.errors import MenuItemNotFoundError, DuplicateMenuItemError, InvalidMenuItemUpdateError, MenuItemRestaurantNotFoundError, CustomerNotFoundError, CartItemNotFoundError,CartNotFoundError,CartRestaurantMismatchError


    
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


    @router.post("/cart/add/{customer_id}/{restaurant_id}/{item_id}/{quantity}", status_code=status.HTTP_201_CREATED)
    def add_item(customer_id: int, restaurant_id: int, item_id: int, quantity: int) -> ShoppingCartRead:
        try:
            return service.cart_add_item_to_cart_service(
                customer_id, restaurant_id, item_id, quantity
            ) 
        except CustomerNotFoundError as e:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
        except MenuItemNotFoundError as e:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
        except CartNotFoundError as e:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
        except ValidationError as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(f"quantity entered equal or blow zero"))
    
    @router.patch("/cart/edit/{customer_id}/{item_id}/{quantity}",
                  status_code=status.HTTP_200_OK)
    def edit_item(customer_id: int, item_id: int, quantity: int) -> ShoppingCartRead:
        try:
            return service.cart_edit_item_to_cart_service(customer_id, item_id, quantity)
        except CustomerNotFoundError as e:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
        except CartItemNotFoundError as e:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
        
       

    @router.delete("/cart/remove/{customer_id}/{item_id}", status_code=status.HTTP_200_OK)
    def remove_item( customer_id:int, item_id:int)  -> ShoppingCartRead:
        try:
            # customer = customer_service.get_customer_by_id(customer_id) # assume customer service exists and has a method to get customer by ID
            
            removed_item = service.cart_remove_item_from_cart_service(customer_id, item_id)
            return removed_item
        except CustomerNotFoundError as e:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
        except CartNotFoundError as e:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
        except CartRestaurantMismatchError as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @router.delete("/cart/clear/{customer_id}", status_code=status.HTTP_200_OK)
    def clear_cart( customer_id:int)  -> ShoppingCartRead:
        try:
            # customer = customer_service.get_customer_by_id(customer_id) # assume customer service exists and has a method to get customer by ID
            cleared_cart = service.cart_empty_items_service(customer_id)
            return cleared_cart
        except CustomerNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found.",
            )
        

    @router.get("/cart/view/{customer_id}", status_code=status.HTTP_200_OK)
    def view_cart( customer_id:int)  -> ShoppingCartRead:
        
        try:
            # customer = app.services.customer_service.get_customer_by_id(customer_id)  # assume customer service exists and has a method to get customer by ID
            cart_items = service.cart_view_by_customer_service(customer_id)
            return cart_items
        except CustomerNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found.",
            )
        

    @router.get("/cart/{customer_id}/calculate_total", status_code=status.HTTP_200_OK)
    def total_cart_price( customer_id:int) -> dict:
        try:
            # customer = app.services.customer_service.get_customer_by_id(customer_id)  # assume customer service exists and has a method to get customer by ID
            total_price = service.total_cart_price_service(customer_id)
        except CustomerNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found.",
            )
        return {"message": f"Total price for cart of user {customer_id}", "total_price": total_price}