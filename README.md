# COSC 310 Team 19 Food Delivery

This is our COSC 310 food-delivery project. Milestone 1 covers restaurant discovery, menu browsing, and restaurant/menu management. Orders and deliveries are planned for later milestones.

## What works right now

- List restaurants, view details, and filter by cuisine through the API.
- Search by name, address, or cuisine in the frontend. Filter by cuisine and availability.
- Create and update restaurant information.
- View menus and individual menu items through the API.
- Add, update, and delete menu items.
- Save restaurant and menu changes in JSON files.
- Check the server with `GET /health`.

The frontend provides customer and restaurant views. Choosing a view is not authentication or authorization; these are outside M1 scope.

## Setup

Use Git and Python 3.12, which matches CI. Run commands from the project root.

```bash
git clone --branch M1-Dev https://github.com/kunoa2580/cosc310-team19-food-delivery.git
cd cosc310-team19-food-delivery
python -m venv .venv
```

Activate the virtual environment:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Install dependencies and start the application:

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Use `python3` instead if that is your system's Python command.

- Frontend: http://127.0.0.1:8000/ui/
- API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

Stop the server with `Ctrl+C`.

## Try the frontend

1. Open `/ui/` and choose **Continue as customer**.
2. Search or filter restaurants, then select **View restaurant** to see details and menu items.
3. Select **Change role**, then **Continue as restaurant**.
4. Create a restaurant, or select an existing restaurant to edit its information and menu.

Restaurant and menu changes submitted through the frontend update the backend's JSON files.

## Current API

Paths are case-sensitive. Restaurant endpoints use `/restaurants`; registered menu endpoints currently use `/restaurant`.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Backend status message |
| GET | `/health` | Health check |
| GET | `/restaurants` | List restaurants |
| GET | `/restaurants/filtered-by-{cuisine}-type` | Case-insensitive exact cuisine match |
| GET | `/restaurants/{restaurant_id}` | Restaurant details |
| POST | `/restaurants` | Create a restaurant |
| PATCH | `/restaurants/{restaurant_id}` | Update supplied restaurant fields |
| DELETE | `/restaurants/{restaurant_id}` | Delete a restaurant |
| GET | `/restaurant/{restaurant_id}/menu-items` | List a restaurant's menu items |
| GET | `/restaurant/{restaurant_id}/menu-items/{item_id}` | Get one menu item |
| POST | `/restaurant/{restaurant_id}/menu-items/create` | Create a menu item |
| PATCH | `/restaurant/{restaurant_id}/menu-items/update/{item_id}` | Update supplied menu-item fields |
| DELETE | `/restaurant/{restaurant_id}/menu-items/delete/{item_id}` | Delete a menu item |

Example request for `POST /restaurants`:

```json
{
  "name": "Example Kitchen",
  "address": "123 Example Street, Kelowna, BC",
  "phone_number": "123-456-7890",
  "email": "hello@example.com",
  "website": "https://example.com",
  "cuisine_type": "Italian",
  "opening_hours": "Mon-Sun: 11:00 AM - 9:00 PM",
  "rating": 4.5,
  "availability": true
}
```

Creation returns `201`; a duplicate restaurant name returns `409`. Missing restaurant details return `404`. Invalid request types or missing required fields normally return `422`.

## Structure and data

`Frontend → FastAPI routes → Services → Repositories → JSON files`

| Path | Purpose |
| --- | --- |
| `app/main.py` | Registers API routes and serves the frontend |
| `app/frontend/` | HTML, CSS, and JavaScript frontend |
| `app/api/routes/` | HTTP requests, responses, and error translation |
| `app/schemas/` | Pydantic request and response models |
| `app/services/` | Business rules and workflow logic |
| `app/repositories/` | Read and write JSON data |
| `data/restaurants.json` | Restaurant records |
| `data/menu_items.json` | Menu-item records linked by restaurant ID |
| `data/uml.md` | Architecture diagrams; some sections need updating |
| `test/` | Backend pytest suite |
| `.github/workflows/ci.yml` | Tests on pushes and pull requests |
| `docs/PROVENANCE.md` | AI assistance record |
| `scrum/` | Team agreement and meeting-note location |

Active repositories use `data/` by default. Set `COSC310_DATA_DIR` to use a separate data directory. The older `menu_repository.py` uses a fixed path and does not respect this setting.

FastAPI serves the frontend, which uses relative API paths. This keeps the frontend and API on the same origin without a separate frontend server.

## Repository structure

```text
cosc310-team19-food-delivery/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── epic.md
│   │   ├── task.md
│   │   └── user_story.md
│   └── workflows/
│       └── ci.yml                      # GitHub Actions tests
├── app/
│   ├── __init__.py
│   ├── main.py                         # FastAPI app and frontend mount
│   ├── errors.py                       # Domain errors
│   ├── api/
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── restaurant_route.py      # Restaurant endpoints
│   │       ├── menu_item_route.py       # Active menu-item endpoints
│   │       └── menu_route.py            # Legacy router; not registered
│   ├── frontend/
│   │   ├── index.html                  # Customer and restaurant views
│   │   ├── styles.css                  # Page styles
│   │   └── app.js                      # Frontend interactions and API calls
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── restaurant.py               # Restaurant Pydantic models
│   │   └── menu_item.py                # Menu-item Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── restaurant_service.py       # Restaurant business logic
│   │   ├── menu_item_service.py        # Active menu-item business logic
│   │   └── menu_service.py             # Legacy menu retrieval
│   └── repositories/
│       ├── __init__.py
│       ├── restaurant_repository.py    # Restaurant JSON persistence
│       ├── menu_item_repository.py     # Active menu-item JSON persistence
│       ├── menu_repository.py          # Legacy menu reader
│       └── json_store.py               # Empty placeholder
├── data/
│   ├── restaurants.json                # Restaurant data
│   ├── menu_items.json                 # Active menu-item data
│   ├── menu_item.json                  # Older, unused data file
│   └── uml.md                          # Architecture diagrams
├── docs/
│   └── PROVENANCE.md                   # AI assistance record
├── scrum/
│   └── team-agreement.md               # Team agreement
├── test/
│   ├── conftest.py                     # Shared fixtures and temporary data
│   ├── test_app.py
│   ├── test_restaurant_route.py
│   ├── test_restaurant_sercive.py       # Existing filename spelling
│   ├── test_restaurant_repository.py
│   ├── test_restaurant_creation_updates.py
│   ├── test_menu_item_route.py
│   ├── test_menu_item_service.py
│   ├── test_menu_item_repo.py
│   └── test_menu_retrieval.py
├── .gitignore
├── requirements.txt
└── README.md
```

This tree reflects the reviewed M1-Dev files, including legacy files still awaiting cleanup. Local folders such as `.venv/`, `__pycache__/`, and `.pytest_cache/` are omitted.

## Tests

With dependencies installed and the virtual environment active:

```bash
python -m pytest -q test/
```

The current suite contains 62 backend tests covering routes, services, repositories, and failure cases. The shared fixture copies representative JSON into a temporary directory for each test. Legacy menu-retrieval tests still read committed data directly, so isolation needs completing.

GitHub Actions installs dependencies and runs tests on pushes and pull requests using Python 3.12. Automated browser tests have not been added yet.

## Known limitations

- Menu creation does not check that the parent restaurant exists. Restaurant deletion does not remove or protect its menu items.
- Explicit null menu updates can save invalid records. Duplicate menu-item renames return `500` instead of `409`.
- Restaurant models need stronger validation for blank values, ratings, and contact fields.
- IDs use the current maximum plus one, so deleting the highest ID allows it to be reused.
- An older menu route/service/repository remains alongside the registered implementation. Its route is unregistered and contains an outdated model import.
- Some OpenAPI descriptions and error responses are missing.

## Development

Create user-story issues with acceptance criteria, work on feature branches, include tests, and request review from another team member before merging. Record AI assistance in `docs/PROVENANCE.md`.

