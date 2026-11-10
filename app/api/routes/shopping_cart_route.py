
from fastapi import APIRouter, HTTPException, status
import app


from app.services.shopping_cart_service import (

    shopping_cart_service,

)



# import app.services.customer_service as customer_service # assume customer service exists and has a method to get customer by ID
# import app.auth as auth # assume auth module exists for authentication and authorization
import app.services.menu_item_service as menu_item_service

router = APIRouter()
service = shopping_cart_service()

class shopping_cart_route:
    
    @router.post("/cart/add/{user_id}/{item_id}/{quantity}?", status_code=status.HTTP_200_OK)
    def add_item(self, user_id, item_id, quantity=1):
        try:
            # customer = customer_service.get_customer_by_id(user_id) # assume customer service exists and has a method to get customer by ID
            item = menu_item_service.get_menu_item_by_id(item_id)
            added_item = service.add_item_to_cart_service(user_id, item_id, quantity)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {user_id} not found.",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu item with ID {item_id} not found.",
            )
        
        return {"message": f"Added {quantity} of item {item_id} to cart for user {user_id}"}

    @router.delete("/cart/remove/{user_id}/{item_id}/{quantity}", status_code=status.HTTP_200_OK)
    def remove_item(self, user_id, item_id, quantity):
        # Logic to remove an item from the shopping cart
        return {"message": f"Removed {quantity} of item {item_id} from cart for user {user_id}"}

    @router.delete("/cart/clear/{user_id}", status_code=status.HTTP_200_OK)
    def clear_cart(self, user_id):
        # Logic to clear the shopping cart for a user
        return {"message": f"Cart cleared for user {user_id}"}

    @router.get("/cart/view/{user_id}", status_code=status.HTTP_200_OK)
    def view_cart(self, user_id) -> dict:
        
        try:
            customer = app.services.customer_service.get_customer_by_id(user_id)  # assume customer service exists and has a method to get customer by ID
            cart_items = service.get_cart_items_service(user_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {user_id} not found.",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Shopping cart for user {user_id} not found.",
            )
        return {"message": f"Viewing cart for user {user_id}", "items": cart_items}

    @router.post("/cart/checkout/{user_id}", status_code=status.HTTP_200_OK)
    def checkout(self, user_id):
        # Logic to checkout the shopping cart
        return {"message": f"Checkout initiated for user {user_id}"}