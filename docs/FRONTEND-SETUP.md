# Simple frontend — installation and running guide

Built against `M1-Dev` commit `719c833` (inspected on October 12, 2026).
The prepared code is on local branch `M1/simple-frontend` in the assistant workspace.
It has not been pushed to GitHub or installed on your computer.

## What is included

| File | Purpose |
| --- | --- |
| app/frontend/index.html | Role screen, restaurant list/details, restaurant and menu forms |
| app/frontend/styles.css | Basic layout, colors and mobile styling |
| app/frontend/app.js | Reads inputs, calls the existing API and displays results/errors |
| app/main.py | Existing application with a /ui static-file mount added |
| docs/FRONTEND-SETUP.md | This guide |
| docs/FRONTEND-PROVENANCE.md | New AI-assisted work record to append to your provenance file |

The download is an overlay of new/changed files, not a complete repository.
It does not contain your data files, virtual environment, Git history, or dependencies.

## 1. Clone into a fresh folder

Open a new VS Code window, then Terminal → New Terminal. Start in a parent folder
where you want the project stored. For example, in Windows PowerShell:

```powershell
cd "E:\Files\UBC\COSC 310\project"
git clone --branch M1-Dev --single-branch https://github.com/kunoa2580/cosc310-team19-food-delivery.git food-delivery-frontend
cd food-delivery-frontend
git switch -c M1/simple-frontend
code -n .
```

Use your own parent directory if that example directory does not exist.
`food-delivery-frontend` must be a new directory. If it already exists, choose
another new name rather than nesting multiple clones inside your old project.
`code -n .` opens this folder in a new VS Code window. You can alternatively use
File → Open Folder if the code command is unavailable.

If you prefer an existing checkout, save/commit your unrelated work first, switch
to your current M1-Dev, pull it, and create a feature branch. The fresh-clone flow
above is the simplest way to avoid mixing this with your previous project folders.

## 2. Extract the ZIP into the project root

Download `food-delivery-simple-frontend.zip` and extract it. Copy its `app/` and
`docs/` folders into `food-delivery-frontend`, merging existing directories.
The destination is the folder that contains `requirements.txt`, `app/`, `data/`
and `test/`.

The new frontend must be located at:

```text
food-delivery-frontend/
├── app/
│   ├── main.py
│   └── frontend/
│       ├── index.html
│       ├── styles.css
│       └── app.js
├── data/
│   ├── restaurants.json
│   └── menu_items.json
├── docs/
│   ├── FRONTEND-SETUP.md
│   └── FRONTEND-PROVENANCE.md
├── test/
└── requirements.txt
```

The ZIP contains a modified `app/main.py` from the inspected M1-Dev commit.
In a fresh clone of that same version, replace the existing main.py. If your
main.py has newer changes, merge the following additions instead of overwriting
those changes:

```python
from fastapi.staticfiles import StaticFiles
from pathlib import Path
```

After your existing `app = FastAPI(...)` and router registration, add:

```python
app.mount(
    "/ui",
    StaticFiles(directory=Path(__file__).resolve().parent / "frontend", html=True),
    name="frontend",
)
```

Do not create another FastAPI application. Do not change the existing restaurant
or menu router prefixes. The frontend uses their current registered paths.

Append the entry in `docs/FRONTEND-PROVENANCE.md` to your existing
`docs/PROVENANCE.md`; preserve your teammates' earlier entries. Add the exact
milestone provenance labels if your instructor provides them separately.

## 3. Create and activate the virtual environment

In the terminal of the NEW project window, verify that you are in the folder
containing requirements.txt:

```powershell
Get-Location
Get-ChildItem
```

If another project environment is active, deactivate it first:

```powershell
deactivate
```

Only use deactivate if an environment is currently active. Then:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks Activate.ps1, you can run the environment's Python directly
without activation or changing system settings:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

In VS Code, Ctrl+Shift+P → Python: Select Interpreter → choose this folder's
`.venv\Scripts\python.exe`. This also helps resolve Python import underlines.

On macOS/Linux use:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

There is no npm install, React setup, Live Server extension, or frontend build.
This frontend is plain HTML/CSS/JavaScript served by FastAPI.

## 4. Choose where to save demo data

Normal mode uses the repository's real `data/restaurants.json` and
`data/menu_items.json`. Creating, editing, and deleting through the website
changes those JSON files.

For a walkthrough that keeps representative data unchanged, copy BOTH JSON files
into a separate existing folder BEFORE starting the server. Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force data-demo
Copy-Item data\restaurants.json data-demo\restaurants.json
Copy-Item data\menu_items.json data-demo\menu_items.json
$env:COSC310_DATA_DIR = (Resolve-Path data-demo).Path
```

Copy those files once. Repeating Copy-Item overwrites earlier demo changes.
The demo directory must exist because the current menu repository does not
create missing parent directories.

For macOS/Linux:

```bash
mkdir -p data-demo
cp data/restaurants.json data/menu_items.json data-demo/
export COSC310_DATA_DIR="$PWD/data-demo"
```

This UI uses the registered menu_item_route and MenuItemRepository, which honor
COSC310_DATA_DIR. It does not use the separate unregistered menu_route module.

## 5. Start the backend and open the frontend

From the project root:

```powershell
python -m uvicorn app.main:app --reload
```

Keep the terminal running. Open:

- Website: http://127.0.0.1:8000/ui/
- API documentation: http://127.0.0.1:8000/docs
- Server health: http://127.0.0.1:8000/health

Use `/ui/` with the trailing slash. Do not double-click index.html or open it
through Live Server. The website and API share the same origin, so relative
fetch URLs work without adding CORS configuration.

## 6. Walk through the customer view

1. Click Continue as customer.
2. See the restaurants returned by GET /restaurants.
3. Search by name, address, or cuisine; choose cuisine and availability filters.
4. Click View restaurant. Details and the real menu are fetched from the backend.
5. Use Restaurants to return to the list. Refresh retrieves current backend data.

Search and the dropdown filters run in app.js against the fetched restaurant list.
The current backend has no general text-search endpoint. Cuisine options come
from the returned data, including cuisine names containing slashes.
Menu items have no artificial sample replacements. Empty menus show an empty state.
Prices are displayed as CAD as a UI convention; the backend price field contains
only a number.

## 7. Walk through the restaurant view

1. Click Change role, then Continue as restaurant.
2. Select a current restaurant to load its information and menu.
3. Change its address or availability and click Save restaurant changes.
4. Add an item with a name, description, price and availability.
5. Click Edit on an item, make a change and click Save item changes.
6. Uncheck Available to deactivate an item without deleting it.
7. Delete removes an item after a confirmation dialog.
8. Click New restaurant to create a separate restaurant. After creation, its menu
   workspace appears and accepts new items.
9. Switch to the customer view to see those changes.
10. Stop the server with Ctrl+C and restart it in the same data mode. Saved changes
    should still be present.

No update request is sent when no form fields changed. PATCH requests contain only
changed fields; false and zero are preserved. The forms send no null values.
Required strings cannot be whitespace-only. HTML number/email/URL checks help the
user fill forms; they do not replace backend validation.

## 8. Which files do the work?

| Action | Existing backend endpoint |
| --- | --- |
| List restaurants | GET /restaurants |
| Restaurant details | GET /restaurants/{restaurant_id} |
| Create restaurant | POST /restaurants |
| Update restaurant | PATCH /restaurants/{restaurant_id} |
| List menu | GET /restaurant/{restaurant_id}/menu-items |
| Add menu item | POST /restaurant/{restaurant_id}/menu-items/create |
| Update menu item | PATCH /restaurant/{restaurant_id}/menu-items/update/{item_id} |
| Delete menu item | DELETE /restaurant/{restaurant_id}/menu-items/delete/{item_id} |

Notice the plural `/restaurants` for restaurant operations and singular
`/restaurant` for menu operations. This matches the code registered in main.py.

The app.js `api()` function sends HTTP requests using fetch and handles HTTP
errors and empty 204 delete responses. Form handlers read the input fields,
call POST/PATCH and refresh the returned data. UI labels are written using
textContent, so API values are displayed as text. The JSON storage is still
managed by your Python repositories; JavaScript does not write JSON files directly.

## 9. Current scope and backend limitations

The entry screen is demo role selection, not account authentication. Anyone who
can access this prototype can choose the restaurant view. The current branch has
no auth/ownership enforcement, customer-account, cart, checkout, order or delivery
endpoints. Those are wider required project features, not features supplied by
this frontend. The simple design follows your previous layout request; no Figma
mockup was supplied to verify visual compliance.

The backend returns 500 rather than 409 for duplicate menu names during an update.
The frontend displays the backend detail instead of claiming that the edit saved.
The backend also does not yet enforce all menu price/current-restaurant rules.
These existing behaviors were left to the team's backend work; the UI does not
claim to provide backend authorization or business-rule enforcement.

## 10. Testing and troubleshooting

Run the project's existing test suite from the root:

```powershell
python -m pytest -q
```

Tests use the existing test fixtures. Manual UI operations use whichever data
folder the server was started with. Use data-demo for demonstrations.

Common problems:

| Problem | Fix |
| --- | --- |
| /ui/ returns 404 | Save the changed main.py, stop the old server and restart in THIS project's root. Check for another Uvicorn process on port 8000. |
| frontend directory does not exist | Verify app/frontend/index.html is in the actual checkout you are running. Avoid app/frontend/frontend nesting. |
| No module named fastapi | Use this project's .venv Python and install requirements.txt. |
| Port 8000 is busy | Stop your earlier server or run `python -m uvicorn app.main:app --reload --port 8001`, then use http://127.0.0.1:8001/ui/. |
| CSS or JavaScript looks outdated | Press Ctrl+F5 in the browser after copying the new files. |
| Data changes appear missing | Confirm COSC310_DATA_DIR points to the same folder after restarting; environment variables apply to the terminal that sets them. |
| Cannot reach the backend | Keep Uvicorn running and open /ui/ from its HTTP URL. |
| API shows a duplicate-name error | Choose another name or keep the existing record's own name. |
| Failed to save menu JSON | Make sure the selected data directory exists and is writable, with menu_items.json copied into it. |

To stop using demo data, first stop Uvicorn, then in PowerShell:

```powershell
Remove-Item Env:COSC310_DATA_DIR -ErrorAction SilentlyContinue
```

On macOS/Linux use `unset COSC310_DATA_DIR`. Restart Uvicorn afterward.

### Verification completed in the assistant workspace

- All 62 existing pytest tests passed.
- JavaScript syntax checks passed.
- /ui/, /ui/styles.css, /ui/app.js and /health returned 200.
- A headless DOM interaction check exercised both role screens, restaurant/menu
  loading, search, cuisine containing a slash, restaurant creation/updates,
  menu creation/updates/deletion, duplicate-name errors and safe text display.
- The interaction check verified changes in copied temporary JSON files.
- A new repository instance loaded the saved changes after the demo process stopped.
- Committed restaurants.json and menu_items.json remained unchanged.
- A real browser binary was unavailable; rendered layout was not visually verified.
  The guide's walkthrough is available for your own browser check.

## 11. Review and share with the team

```powershell
git status
git diff -- app/main.py
git add app/frontend/index.html app/frontend/styles.css app/frontend/app.js app/main.py docs/FRONTEND-SETUP.md docs/FRONTEND-PROVENANCE.md docs/PROVENANCE.md
git commit -m "Add simple restaurant and menu frontend"
git push -u origin M1/simple-frontend
```

Only stage the intended code/docs. If data-demo appears as untracked, leave it out
of the commit. Open a PR against the team's agreed integration branch M1-Dev and
include test results and manual walkthrough evidence. Ask a teammate to review.

## Course requirements applied

The project overview explicitly requires frontend/backend communication, layered
architecture (Section 7), JSON/CSV persistence and isolated test data (Section 8),
pytest (Section 9), feature branches/PRs/peer review (Section 10) and recording
consequential AI assistance in docs/PROVENANCE.md (Section 13).
Lecture 3 explicitly separates HTTP routes, business-rule services and storage
repositories. The static-file mount, vanilla JavaScript, filenames and styling
are implementation choices, not exact rules listed in the PDFs.
The detailed M1 milestone and Figma mockup were not supplied.
