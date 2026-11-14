from app.repositories.shopping_cart_repository import (
    ShoppingCartRepository
)
from app.schemas.shopping_cart import ShoppingCartCreate, ShoppingCartUpdate, ShoppingCartRead, ItemInCartCreate, ItemInCartUpdate, ItemInCartRead
from app.schemas.menu_item import MenuItemRead
from app.services.menu_item_service import menu_service_get_by_id
# from errors import CartItemNotFoundError


repository = ShoppingCartRepository()

    # add_item_to_cart_service,
    # remove_item_from_cart_service,
    # clear_cart_service,
    # get_cart_items_service,
    # total_cart_price_service,

class shopping_cart_service:


    def cart_add_item_to_cart_service(self, customer_id:int, restaurant_id:int, item_id:int, quantity:int) -> dict:
        try:
            
            """{
            "item_id": 2,
            "restaurant_id": 1,
            "name": "Iced Peach Black Tea Lemonade",
            "price": 4.99,
            "availability": true,
            "quantity": 1}
            """
            
            item = menu_service_get_by_id(restaurant_id, item_id)
            item_to_add = ItemInCartCreate(item_id=item.item_id, 
                                           restaurant_id=item.restaurant_id, 
                                           name=item.name ,
                                           price=item.price,
                                           availability=item.availability,
                                           quantity=quantity)
            
            return repository.cart_add_item_to_cart_repo(customer_id, item_to_add.model_dump())
        except Exception as e:
            print(f"Error adding item to cart: {e}")
            return False

    def cart_edit_item_to_cart_service(self, customer_id: int, item_id: int, quantity: int) -> list[dict]:
        cart = repository.cart_edit_item_repo(customer_id, item_id, quantity)
        if cart is None:
            raise Exception(
                f"No item {item_id} in cart for customer {customer_id}"
            )   
        return cart

    def cart_remove_item_from_cart_service(self, customer_id: int, item_id: int) -> bool:
        try:
            return repository.cart_edit_item_repo(customer_id, item_id, 0)
        except Exception as e:
            print(f"Error removing item from cart: {e}")
            return False

    def cart_empty_items_service(self, customer_id: int) -> bool:
        try:
            return repository.cart_empty_items_repo(customer_id)
        except Exception as e:
            print(f"Error clearing cart: {e}")
            return False

    def cart_view_by_customer_service(self, customer_id: int) -> list[dict] | None:
        try:
            cart = repository.cart_view_by_customer_repo(customer_id)
            if cart is None:
                repository.cart_add_customer(customer_id)
            cart = repository.cart_view_by_customer_repo(customer_id)
            return cart
        except Exception as e:
            print(f"Error fetching cart items: {e}")
            return None
    
        
    def total_cart_price_service(self, customer_id: int) -> float | None:
        cart = self.cart_view_by_customer_service(customer_id)
        if not cart:
            return None
        total_price = 0.0
        for item in cart["items"]:
            total_price += float(item["price"]) * float(item["quantity"])
        return total_price
