## Simple restaurant and menu frontend

**Tool:** ChatGPT / Codex (OpenAI)

AI generated app/frontend/index.html, app/frontend/styles.css and app/frontend/app.js,
added the /ui static-file mount to app/main.py, and wrote the frontend setup guide.
The design follows the user's earlier request for a simple customer/restaurant
prototype and uses the API contracts inspected at M1-Dev commit 719c833.

The frontend implements restaurant discovery, client-side search/filters,
restaurant creation/updates and real menu listing/creation/updates/deletion.
The role selector is explicitly a demo; backend authentication is not supplied.
Existing business functions and representative JSON data were not modified.

Verification: the existing pytest suite was run; JavaScript syntax was checked;
headless DOM interaction checks used copied temporary data to test UI requests and
persistence. A browser binary was unavailable, so rendered visual layout was not
verified in a real browser.
Students must review, understand and explain the submitted code. Add the exact
milestone provenance labels from the instructor's detailed instructions when available.
