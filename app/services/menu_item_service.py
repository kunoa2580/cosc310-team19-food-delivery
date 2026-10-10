from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.menu_item import Menu_item_Create, Menu_item_Update, Menu_item_Read
from app.services.restaurant_service import restaurant_service_list
import json


menuRepo = MenuItemRepository()
restRepo = RestaurantRepository()

# @TheTureFADED
def menu_item_service_create(restaurant_id:int, new_menu_item:Menu_item_Create) -> Menu_item_Read:
    
    """ Does not have exception when duplicated happened or does not find the request restaurant_id 
    however this function will create a new menu item toward assinged restaurant_id, and will return the new menu item as a Menu_item_Read object.
    no exception handles
     no status code return
    """
    menu_items = menu_item_service_list()
    next_id = max((i["item_id"] for i in menu_items), default=0)+1
    # print(len(menu_items), "length of menu items")
    # print("menu_items after json" ,type(menu_items))
    temp_data = {"item_id":next_id,"restaurant_id":restaurant_id, **new_menu_item.model_dump()}

    for mi in menu_items:
        if temp_data["name"] == mi["name"] and temp_data["restaurant_id"] == mi["restaurant_id"]:
            raise Exception (f"This item is already in the restaurant")

        
    menu_items.append(temp_data)

    menuRepo.save_all_items(menu_items)
    
    return Menu_item_Read(**temp_data)

# @TheTureFADED
def menu_item_service_list() -> list[dict]:
    """ This function will get all of menu items for all of restaurant """
    menu_items = menuRepo.load_all_items()
    # print("menu_items is" ,  type(menu_items))
    return menu_items

def menu_item_service_create_by_restaurant_name(restaurant_name:str,new_menu_item: Menu_item_Create ) -> Menu_item_Read:
    """ This function will create item by restaurant_name and hand the restaurant id to menu_item_service_create() function and return Menu_item_Read object
     no exception handles
     no status code return
       """
    restaurants = restaurant_service_list()
    restaurant_id = -1
    for r in restaurants: 
        r = r.model_dump()
        if r["name"] == restaurant_name:
            restaurant_id = int(r["id"])
    if restaurant_id == -1:
        raise Exception (f"The restaurant does not exit")
    
    return menu_item_service_create(restaurant_id, new_menu_item)

def menu_item_service_remove_by_id(item_id:int) -> bool:
    menu_items = menu_item_service_list()
    for mi in menu_items:
        if mi["id"] == item_id:
            menu_items.remove(mi)
            menuRepo.save_all_items(menu_items)
            return True
    return False


def menu_item_service_get_by_id():
    pass


def menu_item_service_update():
    pass


def menu_item_service_delete():
    pass


def menu_item_service_get_by_restaurant(restaurant_name:str):
    pass
