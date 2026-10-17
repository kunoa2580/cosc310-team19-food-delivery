# Provenance

This document records the use of generative AI assistance in accordance with the COSC 310 project requirements.

## Generative AI Assistance

**Tool:** ChatGPT (OpenAI)

### 1. Debugging Assistance

AI was used to help diagnose and understand issues related to the pytest testing configuration, particularly `conftest.py`.

Examples:
- Explaining errors involving pytest fixtures and `conftest.py`.
- Helping identify problems with test-data isolation and temporary test directories.
- Suggesting debugging steps for fixture configuration and test setup.

AI assistance was used for debugging and explanation. The resulting code was reviewed, tested, and validated by the team before being included in the repository.

### 2. Markdown and README Formatting

AI was used to assist with formatting project documentation into clear and consistent Markdown.

Examples:
- Formatting the "How to Run Tests" section of `README.md`.
- Formatting the repository structure as a Markdown directory tree.
- Improving headings, code blocks, and organization of README content.

AI assistance in this area was limited to documentation structure, formatting, and presentation. The documented commands and repository structure were reviewed against the actual project before inclusion.

### 3. Frontend Development

**Tool:** ChatGPT / Codex (OpenAI)

AI was used to help generate and edit the frontend in:

- `app/frontend/index.html`
- `app/frontend/styles.css`
- `app/frontend/app.js`

The assistance covered customer and restaurant views, restaurant search and filtering, restaurant details and menus, restaurant creation and updates, menu-item management, form handling, and API feedback messages. AI also helped add the `/ui/` static-file mount in `app/main.py` and remove the demo notice and prototype footer text.

The frontend uses the existing FastAPI endpoints. View selection is a demo navigation feature, not authentication or authorization.

Validation recorded for the M1 review: the 62 existing backend tests passed, and HTTP checks confirmed that `/ui/`, its JavaScript, and its stylesheet are served successfully. These checks do not establish automated browser coverage. Frontend browser tests and a complete browser workflow check still need to be added or recorded.

### 4. M1 Documentation and Requirements Review

**Tool:** ChatGPT / Codex (OpenAI)

AI was used to compare the M1-Dev code, tests, GitHub workflow, issues, and review records against the supplied M1 assignment screenshots. It helped draft user-story descriptions, update the README, and extend this provenance document. The README update includes implementation details and known limitations, in addition to formatting.

The review ran the existing test suite and additional API checks using temporary copies of the JSON data. It identified missing frontend tests, incomplete API documentation, data-integrity problems, and submission/workflow gaps. No fixes to those implementation gaps are claimed by this documentation update.

### 5. M1 Requirements Review

**Tool:** ChatGPT / Codex (OpenAI)

ChatGPT was used to compare the M1-Dev implementation, tests, documentation, and GitHub workflow with the Milestone 1 assignment requirements.

The assistance included:
- Checking restaurant discovery, menu browsing, and management functionality.
- Reviewing architecture, JSON persistence, Pydantic models, and error handling.
- Identifying missing tests, incomplete API documentation, and data-integrity issues.
- Checking GitHub collaboration evidence and submission requirements.
- Suggesting README updates and a checklist of remaining work.

The review identified possible gaps and recommended changes; it did not certify that all M1 requirements were satisfied. The team remains responsible for verifying the findings, testing changes, and explaining the submitted work.
