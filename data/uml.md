## UML diagrams

### Restaurant Backend

```mermaid

classDiagram
    direction TB
    class Application {
        <<module>>
        +app: FastAPI
        +root()
        +health()
    }
    class RestaurantRoutes {
        <<module>>
        +router: APIRouter
        +restaurant_route_get_list(): list~RestaurantRead~
        +restaurant_route_create(new_restaurant: RestaurantCreate): RestaurantRead
        +restaurant_route_get_by_cuisine(cuisine: str or None = None): list~RestaurantRead~
        +restaurant_route_get_by_id(restaurant_id: int): RestaurantRead
        +restaurant_route_delete(restaurant_id: int): None
        +restaurant_route_search(input: str): RestaurantRead or None P
        +restaurant_route_update(restaurant_id: int, updates: RestaurantUpdate): RestaurantRead
    }
    note for RestaurantRoutes "TODO: restaurant_route_update() must return HTTP 404 when the restaurant is not found"
    class RestaurantService {
        <<module>>
        +restaurant_repo: RestaurantRepository
        +restaurant_service_create(new_restaurant: RestaurantCreate): RestaurantRead
        +restaurant_service_list(): list~RestaurantRead~
        +restaurant_service_get_by_id(restaurant_id: int): RestaurantRead
        +restaurant_service_get_by_cuisine(cuisine: str): list~RestaurantRead~
        +restaurant_service_delete(restaurant_id: int): None
        +restaurant_service_search(input: str): RestaurantRead or None P
        +restaurant_service_update(restaurant_id: int, updates: RestaurantUpdate): RestaurantRead 
    }
    class RestaurantRepository {
        <<class>>
        +data_path: str or None
        +__init__(data_path: str or None = None)
        -_get_data_path(): Path
        -_load(): list~dict~
        -_save(restaurants: list~dict~): None
        +restaurant_repo_list(): list~dict~
        +restaurant_repo_get_by_id(restaurant_id: int): dict or None
        +restaurant_repo_create(restaurant_data: dict): dict
        +restaurant_repo_delete_by_id(restaurant_id: int): bool
        +restaurant_repo_search(input: str): dict or None P
        +restaurant_repo_update_by_id(self, restaurant_id: int, updates: dict): dict or None
    }
    Application ..> RestaurantRoutes : includes router
    RestaurantRoutes ..> RestaurantService : calls
    RestaurantService ..> RestaurantRepository : uses restaurant_repo instance

```

### Menu Backend[TODO]

```mermaid
classDiagram
    direction TB
    class MenuRoutes {
        <<module>>
        +router: APIRouter P
        +menu_route_list_items(restaurant_id: int): list~MenuItemRead~ P
        +menu_route_get_by_id(restaurant_id: int, item_id: int): MenuItemRead P
        +menu_route_add_item(restaurant_id: int, payload: MenuItemCreate): MenuItemRead P
        +menu_route_update_item(restaurant_id: int, item_id: int, payload: MenuItemUpdate): MenuItemRead P
    }
    class MenuServices {
        <<module>>
        +menu_repo: MenuRepository P
        +menu_service_list(restaurant_id: int): list~MenuItemRead~ P
        +menu_service_get_by_id(restaurant_id: int, item_id: int): MenuItemRead P
        +menu_service_add(restaurant_id: int, payload: MenuItemCreate): MenuItemRead P
        +menu_service_update(restaurant_id: int, item_id: int, payload: MenuItemUpdate): MenuItemRead P
    }
    class MenuRepository {
        <<class>>
        +data_path: str or None P
        +__init__(data_path: str or None = None) P
        -_get_data_path(): Path P
        -_load(): list~dict~ P
        -_save(records: list~dict~): None P
        +menu_repo_list(restaurant_id: int): list~dict~ P
        +menu_repo_get_by_id(restaurant_id: int, item_id: int): dict or None P
        +menu_repo_create(record: dict): dict P
        +menu_repo_udpate(restaurant_id: int, item_id: int, changes: dict): dict or None P
    }
    MenuRoutes ..> MenuServices : calls
    MenuServices ..> MenuRepository : calls

```


### Current models and domain errors

```mermaid

classDiagram
    direction TB
    class BaseModel {
        <<external>>
    }
    class RestaurantRead {
        <<class>>
        +id: int
        +name: str
        +address: str
        +phone_number: str
        +email: str
        +website: str
        +cuisine_type: str
        +opening_hours: str
        +rating: float
        +availability: bool
    }
    class RestaurantCreate {
        <<class>>
        +name: str
        +address: str
        +phone_number: str
        +email: str
        +website: str
        +cuisine_type: str
        +opening_hours: str
        +rating: float
        +availability: bool = True
    }
    class RestaurantUpdate {
        <<class>>
        +name: str or None = None
        +address: str or None = None
        +phone_number: str or None = None
        +email: str or None = None
        +website: str or None = None
        +cuisine_type: str or None = None
        +opening_hours: str or None = None
        +rating: float or None = None
        +availability: bool or None = None
    }
    class Exception {
        <<external>>
    }
    class DuplicateRestaurantError {
        <<class>>
    }
    class RestaurantNotFoundError {
        <<class>>
    }
    BaseModel <|-- RestaurantRead
    BaseModel <|-- RestaurantCreate
    BaseModel <|-- RestaurantUpdate
    Exception <|-- DuplicateRestaurantError
    Exception <|-- RestaurantNotFoundError

```

### Menu models and domain errors [TODO]

```mermaid
classDiagram
    direction TB

    class BaseModel {
        <<external>>
    }

    class MenuItemRead {
        <<class>>
        +id: int
        +restaurant_id: int
        +name: str
        +description: str
        +price: float
        +availability: bool
    }

    class MenuItemCreate {
        <<class>>
        +name: str
        +description: str
        +price: float
        +availability: bool = True
    }

    class MenuItemUpdate {
        <<class>>
        +name: str or None = None
        +description: str or None = None
        +price: float or None = None
        +availability: bool or None = None
    }

    class Exception {
        <<external>>
    }

    class DuplicateMenuItemError {
        <<class>>
    }

    class MenuItemNotFoundError {
        <<class>>
    }

    class RestaurantNotFoundError {
        <<class>>
    }

    BaseModel <|-- MenuItemRead
    BaseModel <|-- MenuItemCreate
    BaseModel <|-- MenuItemUpdate

    Exception <|-- DuplicateMenuItemError
    Exception <|-- MenuItemNotFoundError
    Exception <|-- RestaurantNotFoundError

    note for MenuItemRead "TODO: implement menu models; price must be nonnegative"
    note for DuplicateMenuItemError "TODO: define duplicate rule; route returns HTTP 409"
    note for MenuItemNotFoundError "TODO: item not found under the specified restaurant; route returns HTTP 404"
    note for RestaurantNotFoundError "Reuse existing error when the parent restaurant does not exist; route returns HTTP 404"
```

`RestaurantNotFoundError` already exists and will be reused.

`restaurant_id` comes from the route URL during creation and updating.
`MenuItemRead` includes both the generated item ID and its restaurant ID.

### Current test modules and fixtures

```mermaid

classDiagram
    direction TB
    class PytestFixtures {
        <<module>>
        +PROJECT_ROOT: Path
        +REAL_DATA: Path
        +isolated_data(tmp_path, monkeypatch)
        +client()
    }
    class ApplicationTests {
        <<module>>
        +client: TestClient
        +test_read_main()
        +test_health()
    }
    class RestaurantRouteTests {
        <<module>>
        +test_get_restaurants_list(client)
        +test_get_restaurants_by_id(client)
        +test_get_by_cuisine(client)
        +test_add_new_restaurants_created(client)
        +test_add_new_restaurants_conflict(client)
        +test_delete_restaurant_not_found(client)
    }
    class RestaurantServiceTests {
        <<module>>
        +sample_data: list~dict~
        +test_restaurant_service_create_good(client)
        +test_restaurant_service_create_conflict(client)
        +test_restaurant_service_list(client)
        +test_restaurant_service_get_by_id_good(client)
        +test_restaurant_service_get_by_id_not_found(client)
        +test_restaurant_service_get_by_cuisine_good(client)
        +test_restaurant_service_get_by_cuisine_not_found(client)
        +test_restaurant_service_delete_good(client)
        +test_restaurant_service_delete_not_found(client)
    }
    class Application {
        <<module>>
    }
    class RestaurantService {
        <<module>>
    }
    RestaurantRouteTests ..> PytestFixtures : uses client and autouse fixture
    RestaurantRouteTests ..> Application : TestClient requests
    ApplicationTests ..> Application : TestClient requests
    RestaurantServiceTests ..> RestaurantService : calls service functions

```
