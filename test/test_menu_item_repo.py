from app.repositories.menu_item_repository import MenuItemRepository


menu_repo = MenuItemRepository()


# def test_all_menu_item_repo():
#     menu_repo.menu_repo_update()
#     menu_repo.menu_repo_create()
#     menu_repo.menu_repo_delete()
#     menu_repo.menu_repo_get_by_id()
#     menu_repo.menu_repo_list()

sample = {
  

    "name": "Iced Peach Green Tea Lemonades",
    "description": "A refreshing blend of green tea, fresh peach syrup, and lemonades.",
    "price": 0.1,
    "availability": False
  
}

def test_menu_repo_list():
    response = menu_repo.menu_repo_list(1)
    assert isinstance(response,list)

def test_menu_repo_get_by_id():
    response = menu_repo.menu_repo_get_by_id(1,1)
    data = response
    assert data ==   {
    "item_id": 1,
    "restaurant_id": 1,
    "name": "Iced Peach Green Tea Lemonade",
    "description": "A refreshing blend of green tea, fresh peach syrup, and lemonade.",
    "price": 0.0,
    "availability": True
  }

    bad_reponse = menu_repo.menu_repo_get_by_id(1000000000,100000000)
    assert bad_reponse == None


def test_menu_repo_delete():
    response = menu_repo.menu_repo_delete(1,1)
    assert response == True
    bad_response = menu_repo.menu_repo_delete(123,132)
    assert bad_response == False


def test_menu_repo_create():
    response = menu_repo.menu_repo_create(sample, 3)
    assert isinstance(response, dict)

    
def test_menu_repo_update():
    response = menu_repo.menu_repo_update(3,1,sample)
    assert response == None
    before = menu_repo.menu_repo_get_by_id(1,1)
    assert before ==  {
    "item_id": 1,
    "restaurant_id": 1,
    "name": "Iced Peach Green Tea Lemonade",
    "description": "A refreshing blend of green tea, fresh peach syrup, and lemonade.",
    "price": 0.0,
    "availability": True
  }
    after = menu_repo.menu_repo_update(1,1,sample)
    assert after == {    'item_id': 1, 'restaurant_id': 1,"name": "Iced Peach Green Tea Lemonades",
    "description": "A refreshing blend of green tea, fresh peach syrup, and lemonades.",
    "price": 0.1,
    "availability": False}
