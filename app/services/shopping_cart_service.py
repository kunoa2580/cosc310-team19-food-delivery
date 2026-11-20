from typing import Protocol


from app.schemas.shopping_cart import ShoppingCartRead, ItemInCartCreate

from app.services.menu_item_service import menu_service_get_by_id
from app.services.account_service import require_active_customer
from app.errors import (
                        CartItemNotFoundError,
                        CartNotFoundError,
                        CartRestaurantMismatchError,
                        MenuItemIsNotAvailableError)


class CartStore(Protocol):
    def cart_view_by_customer_repo(self, customer_id: int) -> dict | None: ...
    def cart_add_item_to_cart_repo(self, customer_id: int, item: dict) -> dict | None: ...
    def cart_edit_item_repo(self, customer_id: int, item_id: int, quantity: int) -> dict | None: ...
    def cart_empty_items_repo(self, customer_id: int) -> dict | None: ...
    def cart_add_customer(self, customer_id: int) -> bool: ...
    def cart_close_repo(self, customer_id: int) -> dict | None:...
""" Desgin approach  """

class shopping_cart_service():
    DELIVERY_FEE = 0


    def __init__(self, repository: CartStore):
        self.repository = repository
        


    def cart_add_item_to_cart_service(self, customer_id:int, restaurant_id:int, item_id:int, quantity:int) -> ShoppingCartRead:
        
        repository = self.repository
        customer = require_active_customer(customer_id)
        
        cart = repository.cart_view_by_customer_repo(customer_id)
        if cart is None:
            repository.cart_add_customer(customer_id)
            cart = repository.cart_view_by_customer_repo(customer_id)
        item = menu_service_get_by_id(restaurant_id, item_id)
        if item.availability is False:
            raise MenuItemIsNotAvailableError(f"Menu item {item_id} is not available")
        if len(cart["items"]) > 0 and item.restaurant_id != cart["items"][0]["restaurant_id"]:
            raise CartRestaurantMismatchError(f"item is not from same Restaurant")
            
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
        cart = repository.cart_add_item_to_cart_repo(customer_id, item_to_add.model_dump())
        return self._to_read(cart)


    def cart_edit_item_to_cart_service(self, customer_id: int, item_id: int, quantity: int) -> ShoppingCartRead:
        repository = self.repository
        require_active_customer(customer_id)

        cart = repository.cart_edit_item_repo(customer_id, item_id, quantity)
        if cart is None:
            raise CartItemNotFoundError(
                f"No item {item_id} in cart for customer {customer_id}"
            )
        return self._to_read(cart)

    def cart_remove_item_from_cart_service(self, customer_id: int, item_id: int) -> ShoppingCartRead:
        repository = self.repository
        customer = require_active_customer(customer_id)
        cart = repository.cart_edit_item_repo(customer_id, item_id, 0)
        if cart is None:
            raise CartItemNotFoundError(
                f"No item {item_id} in cart for customer {customer_id}"
            )
        return self._to_read(cart)

    def cart_empty_items_service(self, customer_id: int) -> ShoppingCartRead:
        repository = self.repository
        customer = require_active_customer(customer_id)
        cart = repository.cart_empty_items_repo(customer_id)

        if cart is None:
            raise CartNotFoundError(f"No cart for customer {customer_id}")
        return self._to_read(cart)

    def cart_view_by_customer_service(self, customer_id: int) -> ShoppingCartRead:
        repository = self.repository
        require_active_customer(customer_id)

        cart = repository.cart_view_by_customer_repo(customer_id)
        if cart is None:
            raise CartNotFoundError(f"No cart for customer {customer_id}")
        return self._to_read(cart)

        

    def _to_read(self, cart: dict) -> ShoppingCartRead:
        
        subtotal = sum(line["price"] * line["quantity"] for line in cart["items"])
        total = subtotal + (self.DELIVERY_FEE if cart["items"] else 0.0)
        return ShoppingCartRead(**cart, subtotal=round(subtotal, 2), total=round(total, 2))
    
    
    def total_cart_price_service(self, customer_id: int) -> float:
        require_active_customer(customer_id)
        cart = self.cart_view_by_customer_service(customer_id)
        return cart.total
    
    # checkout service call for 
    def cart_close_service(self, customer_id: int) -> ShoppingCartRead:
        require_active_customer(customer_id)
        cart = self.repository.cart_close_repo(customer_id)
        if cart is None:
            raise CartNotFoundError(f"No active cart for customer {customer_id}")
        return self._to_read(cart)