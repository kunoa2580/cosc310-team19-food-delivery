import json
import os


class ShoppingCartRepository:
    """ 
    ```
    _get_data_path 
    
    ```
    return data_path string
    ```
    _load
    ``` 
    data [shopping cart with customer_id, cart_id, items:[{...}, {...}]] return as list[dict]
    load data helper called from service with given customer_id


    ```
    _save
    ```
    to save updated/edited/deleted/added data give with data have been edited/deleted/updated opetions

   

     sample data strcutre in cart for one user
     Json structure for a shopping cart:
     ```
        {
        "cart_id": 1,
        "customer_id": 1,
        "items": [
            {
                "item_id": 2,
                "restaurant_id": 1,
                "name": "Iced Peach Black Tea Lemonade",
                "description": "A refreshing blend of Black tea, fresh peach syrup, and lemonade.",
                "price": 4.99,
                "availability": true,
                "quantity": 1
            },
            {
                "item_id": 1,
                "restaurant_id": 1,
                "name": "Really Small Hamburger",
                "description": "A juicy beef patty served on a toasted bun with lettuce, tomato, and special sauce.",
                "price": 10.99,
                "availability": true,
                "quantity": 2
            }
        ]
    }
    ```

```    for customer carts in all carts
        if customer id 
            retrun customer cart
            
    ```
    



    """
    def __init__(self, data_path: str | None = None):
        self.data_path = data_path

    def _get_data_path(self) -> str:
        """ get data path 
         
        return cart path string
        """
        if self.data_path is not None:
            return self.data_path

        data_dir = os.getenv("COSC310_DATA_DIR", "data")

        return os.path.join(data_dir, "shopping_cart.json")


    def _load(self) -> list[dict]:
        """ get data path and convert json to list [dict] with all customer carts data
        
        retrun ```list[dict]```
        
        """
        data_path = self._get_data_path()
        if not os.path.exists(data_path):
            return []

        with open(data_path, "r", encoding="utf-8") as f:
            
            return json.load(f)
        


    def _save(self, records: list[dict]) -> None:
        data_path = self._get_data_path()

        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)
    
    def cart_add_customer(self,customer_id:int) -> bool:
        all_carts = self._load()
        for cart in all_carts:
            if cart["customer_id"] == customer_id:
                return False
        new_cart = {
            "cart_id": len(all_carts) + 1,
            "customer_id": customer_id,
            "items": [],
            "checkout_status": False
        }
        all_carts.append(new_cart)
        self._save(all_carts)
        return True


    def cart_add_item_to_cart_repo(self, customer_id: int, item: dict) -> dict | None:
        all_carts = self._load()
        for cart in all_carts:
            if cart["customer_id"] == customer_id:
            
                existing = None
                for line in cart["items"]:
                    if line["item_id"] == item["item_id"]:
                        existing = line
                        break
                    
                if existing is None:
                    cart["items"].append(item)
                else:
                    existing["quantity"] += item["quantity"]
    
                self._save(all_carts)
                return cart
        return None

    def cart_edit_item_repo(self, customer_id:int, item_id: int, quantity: int) -> list[dict] | None:
        all_carts = self._load()
        for cart in all_carts:  
            if cart["customer_id"] == customer_id:
                for cart_item in cart["items"]:
                    if cart_item["item_id"] == item_id:
                        if quantity <= 0:
                            cart["items"].remove(cart_item)
                        cart_item["quantity"] = quantity
                        self._save(all_carts)
                        return cart["items"]
        return None

    def cart_empty_items_repo(self ,customer_id:int) -> bool:
        all_carts = self._load()
        for cart in all_carts:
            if cart["customer_id"] == customer_id:
                cart["items"] = []
                self._save(all_carts)
                return True
        return False

    def cart_view_by_customer_repo(self, customer_id:int) -> list[dict] | None:
        all_carts = self._load()
        for cart in all_carts:
            if cart["customer_id"] == customer_id:
                return cart
        return None



    
