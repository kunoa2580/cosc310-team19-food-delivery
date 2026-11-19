import random
from app.repositories.shopping_cart_repository import (
    ShoppingCartRepository
)
from app.schemas.shopping_cart import ShoppingCartCreate, ShoppingCartUpdate, ShoppingCartRead, ItemInCartCreate, ItemInCartUpdate, ItemInCartRead
from app.schemas.menu_item import MenuItemRead
from app.services.menu_item_service import menu_service_get_by_id
from app.errors import MenuItemNotFoundError, DuplicateMenuItemError, InvalidMenuItemUpdateError, MenuItemRestaurantNotFoundError, CustomerNotFoundError, CartItemNotFoundError,CartNotFoundError,CartRestaurantMismatchError
# from errors import CartItemNotFoundError
# Fake customer service
class customer_service:
    def get_customer_by_id(customer_id:int) -> bool:
        if customer_id <= 5:
            return True
        return False


repository = ShoppingCartRepository()



class shopping_cart_service:


    def cart_add_item_to_cart_service(self, customer_id:int, restaurant_id:int, item_id:int, quantity:int) -> ShoppingCartRead:
        customer = customer_service.get_customer_by_id(customer_id)
        cart = repository.cart_view_by_customer_repo(customer_id)
        if customer is False:
            raise CustomerNotFoundError(f"Customer {customer_id} is not found")
        if cart is None:
            raise CartNotFoundError(f"No cart for customer {customer_id}")
        item = menu_service_get_by_id(restaurant_id, item_id)
        
            
        """{
        "item_id": 2,
        "restaurant_id": 1,
        "name": "Iced Peach Black Tea Lemonade",
        "price": 4.99,
        "availability": true,
        "quantity": 1}
        """
        item_to_add = ItemInCartCreate(item_id=item.item_id, 
                                       restaurant_id=item.restaurant_id, 
                                       name=item.name ,
                                       price=item.price,
                                       availability=item.availability,
                                       quantity=quantity)
        # repository.cart_add_item_to_cart_repo(customer_id, item_to_add.model_dump())
        return ShoppingCartRead(**repository.cart_add_item_to_cart_repo(customer_id, item_to_add.model_dump()))


    def cart_edit_item_to_cart_service(self, customer_id: int, item_id: int, quantity: int) -> ShoppingCartRead:
        if customer_service.get_customer_by_id(customer_id) is False:
            raise CustomerNotFoundError(f"Customer {customer_id} is not found")

        cart = repository.cart_edit_item_repo(customer_id, item_id, quantity)
        if cart is None:
            raise CartItemNotFoundError(
                f"No item {item_id} in cart for customer {customer_id}"
            )
        return ShoppingCartRead(**cart)

    def cart_remove_item_from_cart_service(self, customer_id: int, item_id: int) -> ShoppingCartRead:
        cart = repository.cart_edit_item_repo(customer_id, item_id, 0)
        if cart is None:
            raise CartItemNotFoundError(
                f"No item {item_id} in cart for customer {customer_id}"
            )
        return ShoppingCartRead(**cart)

    def cart_empty_items_service(self, customer_id: int) -> ShoppingCartRead:
        cart = repository.cart_empty_items_repo(customer_id)
        if cart is None:
            raise CartNotFoundError(f"No cart for customer {customer_id}")
        return ShoppingCartRead(**cart)

    def cart_view_by_customer_service(self, customer_id: int) -> ShoppingCartRead:
        if customer_service.get_customer_by_id(customer_id) is False:
            raise CustomerNotFoundError(f"Customer {customer_id} is not found")
        cart = repository.cart_view_by_customer_repo(customer_id)
        if cart is None:
            repository.cart_add_customer(customer_id)
            cart = repository.cart_view_by_customer_repo(customer_id)
        return ShoppingCartRead(**cart)
    
    
    def total_cart_price_service(self, customer_id: int) -> float:
        cart = self.cart_view_by_customer_service(customer_id)
        if cart is None:
            raise CustomerNotFoundError(f"Customer {customer_id} is not found")
        return sum(line.price * line.quantity for line in cart.items)