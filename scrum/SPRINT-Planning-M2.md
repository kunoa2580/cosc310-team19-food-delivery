# Sprint Planning M2

## Sprint Information

- **Sprint / Milestone:** Milestone 2 (M2) – Integrated Core System
- **Sprint dates:** 2026-10-31 to 2026-11-20 (end of Week 11)
- **Planning meeting date:** 2026-10-30, 7:30 p.m. (Discord voice chat)
- **Facilitator:** [Name]

### Team Members

- [ ] Lucas Liu – Customer accounts and authentication
- [ ] Allan Zhang – Shopping cart
- [ ] Xingyu Tang – Checkout and orders

> The team now has three members, so M2 work is divided into three vertical slices instead of four.

---

## 1. Sprint Goal

> What should the team have working by the end of this sprint?

**Sprint Goal:**

Connect the separate subsystems into one working Customer → Restaurant → Menu → Cart → Checkout → Order workflow, with authentication and business rules enforced by the backend. Keep all M1 restaurant and menu features working, and have each member make one architectural improvement found during integration.

---

## 2. Sprint Backlog

Select the user stories that the team commits to working on during this sprint.

| User Story | Description | Priority | Primary Owner | Dependencies |
|---|---|---|---|---|
| #62–#65 | Restaurant and menu features from M1 (discover, details, browse menu, create/update). Keep them working after integration. | Medium | All team members | None; already delivered in M1. |
| #66–#70 | Customer accounts: register, sign in, view and update profile and address, deactivate. | High | Lucas Liu | None. Cart and orders depend on it. |
| #71–#74 | Authentication and authorization: identify the signed-in user, enforce roles, return 401/403. | High | Lucas Liu | #66–#70 |
| #75–#81 | Shopping cart: create or get the active cart, add, update, remove, clear, view, backend total. | High | Allan Zhang | #66–#74 (signed-in customer), #64 (menu items) |
| #82–#87 | Checkout: validate customer, cart and menu, recalculate prices, create and save the order, then clear the cart. | High | Xingyu Tang | #66–#74, #75–#81 |
| #88–#90 | Orders: view one order, view order history, keep price snapshots for historical integrity. | High | Xingyu Tang | #82–#87 |

> **Important:** Primary ownership means that the student is responsible for coordinating the work. It does not mean that the student works alone or that other team members cannot contribute.

---

## 3. Task Decomposition

Break larger user stories into smaller tasks that can be implemented, reviewed, and tested.

### User Stories #66–#74 — Customer Accounts and Authentication (Lucas Liu)

- [ ] Account schemas, repository and service: register, view profile, update name and delivery address, deactivate.
- [ ] Store passwords as hashes; never return credentials in API responses.
- [ ] Login that returns a session token; token expiry and logout.
- [ ] Shared route dependencies: current account, current customer, owner check, role check.
- [ ] Global handlers that turn account errors into 401/403/404/409.
- [ ] Tests: registration, login failure, token expiry, accessing another customer's data, deactivated account.
- [ ] Documentation / API updates: README section on sign-in and roles; OpenAPI error responses.

### User Stories #75–#81 — Shopping Cart (Allan Zhang)

- [ ] Cart repository: one active cart per customer, merge repeated items, empty and close the cart.
- [ ] Cart service: only one restaurant per cart, reject unavailable or unknown menu items, valid quantities.
- [ ] Backend calculates the subtotal and total; the frontend only displays them.
- [ ] Cart routes use the signed-in customer instead of a customer id in the URL.
- [ ] Service functions for checkout to read and clear the cart.
- [ ] Tests: repository, service rules (mixed restaurants, unavailable item, totals), route status codes.
- [ ] Documentation / API updates: cart endpoints in README and OpenAPI; cart page in the frontend.

### User Stories #82–#90 — Checkout and Orders (Xingyu Tang)

- [ ] Order schemas and order repository (`data/orders.json`, id = largest id + 1).
- [ ] `order_service_checkout`: validate everything first, read current menu prices, save the order, then clear the cart.
- [ ] Copy item name and unit price into the order so old orders keep their price.
- [ ] Order routes: checkout, view one order, order history, with owner checks.
- [ ] Connect to the account and cart services after they are merged.
- [ ] Tests: repository, service (save failure, price change), routes (401/403/404), one real cart-to-order integration test.
- [ ] Documentation / API updates: order endpoints in README; known limitation about cart clearing failure.

### Shared Work (All team members)

- [ ] Keep M1 restaurant and menu features working after integration (#62–#65).
- [ ] Connect the frontend to the full workflow: sign in, browse, cart, checkout, view order.
- [ ] Each member picks one weakness found during integration, opens an issue, and fixes it in a separate PR with tests.
- [ ] Each member adds at least one multi-subsystem test and one regression test.
- [ ] Review at least one teammate's PR per slice.
- [ ] Record each architectural improvement in the Decision Receipt during the lab.

---

## 4. Dependencies and Integration

Identify work that depends on another team member, subsystem, or component.

| Dependency | Related User Stories | Who is Responsible? | Planned Resolution |
|---|---|---|---|
| Cart and order routes need the signed-in customer | #71–#74, #75–#90 | Lucas Liu | Merge authentication first; other routes use the shared dependencies. |
| Cart needs current menu items and their availability | #75–#81, #64 | Allan Zhang | Cart service calls the existing menu service instead of copying menu data. |
| Checkout needs to know if the customer is active | #82, #66–#70 | Lucas Liu, Xingyu Tang | Checkout calls the account service through one small function, mocked in tests until accounts are merged. |
| Checkout needs to read and clear the cart | #82, #86, #75–#81 | Allan Zhang, Xingyu Tang | Agree on the cart service functions; checkout uses them through small adapter functions. |
| Restaurant and menu changes need role checks | #65, #72 | Lucas Liu, All team members | Use the shared role dependency on restaurant and menu management endpoints. |
| Frontend needs all endpoints | All | All team members | Connect the frontend after the integration branch passes all tests. |

### Integration Plan

Each story is developed on its own feature branch and merged into `M2-Dev` through a reviewed pull request. Accounts are merged first, then the cart, then checkout and orders are connected on a shared integration branch where the full workflow is tested. When everything passes, `M2-Dev` is merged into `main` and tagged `m2-integrated-system`.

---

## 5. Risks and Potential Blockers

Identify anything that could prevent the team from achieving the sprint goal.

| Risk / Blocker | Impact | Planned Action | Owner |
|---|---|---|---|
| The team has only three members | More work per person. | Split by vertical slice and keep each PR small. | All team members |
| Authentication is late | Cart and orders cannot use real customers. | Merge accounts first; others build against agreed function names. | Lucas Liu |
| Cart interface changes during integration | Checkout and tests break. | Announce cart API changes in the group chat before merging. | Allan Zhang |
| Interfaces between slices do not match | Integration breaks late in the sprint. | Agree on function names and data formats early; write an integration test. | All team members |
| Merge conflicts in shared files (`main.py`, `errors.py`, `app.js`) | Lost time during integration. | Merge `M2-Dev` into feature branches often; tell the team before editing shared files. | Each contributor |
| Test or demo data committed into `data/*.json` | Wrong data shows up in the demo. | Tests use a temporary data folder; check `git status` before committing. | Each contributor |
| Missing AI records | Incomplete provenance documentation. | Add entries to `docs/PROVENANCE.md` as work is done. | Each contributor |

---

## 6. Definition of Done

For work to be considered **DONE**, the team agrees that it must satisfy the following:

- [ ] Requirements/acceptance criteria are satisfied.
- [ ] Business logic is implemented in the appropriate service layer.
- [ ] Persistence is handled through the repository layer.
- [ ] Appropriate unit tests are included.
- [ ] Appropriate integration/API tests are included.
- [ ] Tests pass.
- [ ] Code has been reviewed by at least one teammate.
- [ ] Review feedback has been addressed.
- [ ] Documentation has been updated where necessary.
- [ ] The change is integrated into the team's working version.
- [ ] No known critical defects remain.

---

## 7. Sprint Commitment

Before ending the meeting, each team member should confirm their understanding of the sprint plan.

| Team Member | Initial Responsibilities | Confirmed |
|---|---|---|
| Lucas Liu | Customer accounts, sign-in, authorization dependencies and error handlers; auth frontend; one architectural improvement. | ☐ |
| Allan Zhang | Shopping cart repository, service and routes; cart frontend; one architectural improvement. | ☐ |
| Xingyu Tang | Checkout, order repository/service/routes, order integration test; one architectural improvement. | ☐ |

---

## Meeting Notes

- We reviewed the M2 requirements and the rubric.
- Since the team now has three members, we split the work into three slices: Lucas takes accounts and authentication, Allan takes the shopping cart, and Xingyu takes checkout and orders.
- Accounts and authentication are merged first because the cart and orders depend on them.
- Lucas will use session tokens; deactivating an account ends its sessions, and the backend re-checks account status on protected requests.
- Allan's cart will use the signed-in customer from the token, allow items from only one restaurant, and calculate totals in the backend.
- Xingyu's checkout will start with small adapter functions for the customer and cart, so it can be built and tested before the other slices are merged.
- Prices at checkout always come from the current menu, not the cart, and the cart is cleared only after the order is saved.
- Restaurant and menu features from M1 stay shared; anyone who changes them asks the team first.
- `M2-Dev` is the integration branch. At the end, it is merged into `main` and tagged `m2-integrated-system`.
- Each member will make one architectural improvement, add a multi-subsystem test and a regression test, and record the improvement in the Decision Receipt.
- We will keep recording AI assistance in `docs/PROVENANCE.md`, including help with this planning document.
