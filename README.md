# COSC 310 Team 19 Food Delivery

This is our team project for COSC 310. The goal is to build a food delivery app that satisfies common food delivery app functions, where customers can find restaurants, view menus, place orders, and follow their deliveries.

## What works right now

- Get the list of restaurants.
- Get one restaurant by its ID.
- Filter restaurants by `cuisine_type` using an exact match.
- Add a restaurant. The app assigns it the next numeric ID and saves it to `data/restaurants.json`.
- Reject a new restaurant and produces 409 CONFLICT if another restaurant already has the same name.
- Check that the server is running with `GET /health`.

## Set up the backend

Python 3.10.0 and Git is required. Run these commands from the project root (the folder containing `requirements.txt` and `data/`).

```bash
git clone https://github.com/kunoa2580/cosc310-team19-food-delivery-1
cd cosc310-team19-food-delivery
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS or Linux
source .venv/bin/activate
```

## Dependency Installation
Run the next commands in the same terminal:

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to try the API in your browser. The app runs at `http://127.0.0.1:8000`. Stop it with `Ctrl+C`.

If `python` is not the command for Python on your computer, use `python3` (on mac) in the commands above.

## Current API

| Method | Path | What it does |
| --- | --- | --- |
| `GET` | `/` | Returns a message that the backend is running. |
| `GET` | `/health` | Returns `{"status": "ok"}`. |
| `GET` | `/Restaurants` | Returns all restaurants. |
| `GET` | `/Restaurants/filtered-by-{cuisine}-type` | Returns restaurants whose cuisin is of `cuisine_type`. |
| `GET` | `/Restaurants` | Also returns all restaurants. |
| `GET` | `/Restaurants/{restaurant_id}` | Returns a restaurant by numeric ID. |
| `DELETE` |  `/Restaurants/{restaurant_id} | Delete a restaurant according to numeric ID. |
| `POST` | `/Restaurants` | Adds a restaurant and returns it with a new ID. |

To add a restaurant, open `/docs`, find `POST /restaurants`, and select **Try it out**. The request body needs these fields:

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
  "availability": True
}
```

The POST route returns HTTP `201` when a restaurant is added and HTTP `409` if the same name already exists. 

## Project folders

| Path | Purpose |
| --- | --- |
| `app/main.py` | Starts the FastAPI app and includes the restaurant routes. |
| `app/api/routes/restaurant_route.py` | Handles restaurant HTTP requests. |
| `app/schemas/restaurant.py` | Defines the restaurant request and data fields. |
| `app/services/restaurant_service.py` | Handles restaurant rules, including duplicate names and new IDs. |
| `app/repositories/restaurant_repository.py` | Reads and writes restaurant data. |
| `data/restaurants.json` | Stores the restaurant list. |
| `requirements.txt` | Lists the Python packages needed to run the backend. |

## Location of representative data

The restaurant request goes from the route to the service, then to the repository, which reads or updates the JSON file. To prevent any misuse or meddling with original data, the repository uses the relative path `data/restaurants.json`.

# Testing and Repository Structure

## How to Run Tests

From the project root, create and activate a virtual environment, then
install the required dependencies.

### macOS / Linux

``` bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

### Windows

``` bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest
```

To run the tests with less output:

``` bash
pytest -q
```

The test suite is located in the `test/` directory. Tests use separate
test data so that the application's committed data is not modified
during testing.

## Repository Structure

``` text
cosc310-team19-food-delivery/
├── app/
│   ├── main.py                      # FastAPI application entry point
│   ├── errors.py                    # Application/domain errors
│   │
│   ├── api/
│   │   └── routes/
│   │       └── restaurant_route.py  # Restaurant HTTP/API endpoints
│   │
│   ├── schemas/
│   │   └── restaurant.py            # Pydantic restaurant models
│   │
│   ├── services/
│   │   └── restaurant_service.py    # Restaurant business logic
│   │
│   └── repositories/
│       ├── restaurant_repository.py # Restaurant persistence operations
│       └── json_store.py             # Shared JSON storage support
│
├── data/
│   ├── restaurants.json             # Persistent restaurant data
│   └── uml.md                       # Architecture/UML documentation
│
├── test/
│   ├── conftest.py                  # Shared pytest fixtures/configuration
│   ├── test_app.py                  # Application-level tests
│   └── test_restaurant_route.py     # Restaurant API tests
│
├── scrum/
│   └── team-agreement.md            # Team agreement
│
├── requirements.txt                 # Python dependencies
├── .gitignore
└── README.md
```

The backend follows the required layered structure:

`Routes → Services → Repositories → JSON persistence`

Routes handle HTTP/API communication, services contain business logic,
and repositories handle persistence.

