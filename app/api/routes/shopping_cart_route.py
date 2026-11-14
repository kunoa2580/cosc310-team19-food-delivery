from fastapi import APIRouter, HTTPException, status
import app


from app.services.shopping_cart_service import (

    shopping_cart_service,

)

# import app.services.customer_service as customer_service # assume customer service exists and has a method to get customer by ID
# import app.auth as auth # assume auth module exists for authentication and authorization
import app.services.menu_item_service as menu_item_service
from app.schemas.shopping_cart import ItemInCartCreate, ItemInCartRead, ShoppingCartCreate,ShoppingCartRead, ShoppingCartUpdate
router = APIRouter()
service = shopping_cart_service()


class shopping_cart_route:
    """ 
    create or retrieve the active cart for a customer;

    add menu items;

    update item quantities;

    remove menu items;

    clear the cart;

    retrieve current cart contents;

    retrieve authoritative subtotal and total values calculated by the backend. 
      
    """
    

    @router.post("/cart/add/{customer_id}/{restaurant_id}/{item_id}/{quantity}", status_code=status.HTTP_201_CREATED, response_model=list[ItemInCartCreate])
    def add_item( customer_id:int, restaurant_id:int, item_id:int, quantity:int=1):
        try:
            # customer = customer_service.get_customer_by_id(customer_id) # assume customer service exists and has a method to get customer by ID
            
            
            added_item = service.cart_add_item_to_cart_service(customer_id, restaurant_id, item_id, quantity)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found.",
            )
        # return {"message": f"Added {quantity} of item {item_id} to cart for user {customer_id}"}
        return added_item
    
    @router.patch("/cart/edit/{customer_id}/{item_id}/{quantity}", status_code=status.HTTP_200_OK, response_model=ShoppingCartUpdate)
    def edit_item( customer_id:int,  item_id:int, quantity:int=1):
        try:
            # customer = customer_service.get_customer_by_id(customer_id) # assume customer service exists and has a method to get customer by ID
            if quantity <= 0:
                edited_item = service.cart_remove_item_from_cart_service(customer_id, item_id)
            else:
                edited_item = service.cart_edit_item_to_cart_service(customer_id,item_id, quantity)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found.",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu item with ID {item_id} not found.",
            )
        
        return {"message": f"edited {quantity} of item {item_id} to cart for user {customer_id}"}

    @router.delete("/cart/remove/{customer_id}/{item_id}", status_code=status.HTTP_200_OK)
    def remove_item( customer_id:int, item_id:int):
        try:
            # customer = customer_service.get_customer_by_id(customer_id) # assume customer service exists and has a method to get customer by ID
            
            removed_item = service.cart_remove_item_from_cart_service(customer_id, item_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu item with ID {item_id} not found.",
            )
        return {"message": f"Removed item {item_id} from cart for user {customer_id}"}

    @router.delete("/cart/clear/{customer_id}", status_code=status.HTTP_200_OK)
    def clear_cart( customer_id:int):
        try:
            # customer = customer_service.get_customer_by_id(customer_id) # assume customer service exists and has a method to get customer by ID
            cleared_cart = service.cart_empty_items_service(customer_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found.",
            )
        return {"message": f"Cart cleared for user {customer_id}"}

    @router.get("/cart/view/{customer_id}", status_code=status.HTTP_200_OK)
    def view_cart( customer_id:int) -> dict:
        
        try:
            # customer = app.services.customer_service.get_customer_by_id(customer_id)  # assume customer service exists and has a method to get customer by ID
            cart_items = service.cart_view_by_customer_service(customer_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found.",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Shopping cart for user {customer_id} not found.",
            )
        return {"message": f"Viewing cart for user {customer_id}", "items": cart_items}

    @router.get("/cart/{customer_id}/calculate_total", status_code=status.HTTP_200_OK)
    def total_cart_price( customer_id:int) -> dict:
        try:
            total_price = service.total_cart_price_service(customer_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found.",
            )
        return {"message": f"Total price for cart of user {customer_id}", "total_price": total_price}