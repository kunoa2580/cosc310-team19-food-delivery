# Sprint Planning M2

## Sprint Information

- **Sprint / Milestone:** Milestone 2 (M1)
- **Sprint dates:** To be confirmed after Friday's lab.
- **Planning meeting date:** 2026-10-30, 7:30 p.m.
- **Facilitator:** Not recorded.

### Team Members

- [ ] Lucas Liu
- [ ] Allan Zhang
- [ ] Xingyu Tang
- [ ] Jingyuan Peng

---

## 1. Sprint Goal

> What should the team have working by the end of this sprint?

**Sprint Goal:**

Complete the M2 workflow from the frontend through the backend to saved data and back. Build and check the backend first, then connect the frontend. Share work more evenly by assigning each person one or a few functions and the related work across the four backend layer

---

## 2. Sprint Backlog

Select the user stories that the team commits to working on during this sprint.

### Restaurant and Menu

| User Story | Description | Priority | Primary Owner | Dependencies |
|---|---|---|---|---|
| # 62 | discover, search, and filter restaurants | High / Medium / Low | | |
| # 63 | retrieve restaurant details | High / Medium / Low | | |
| # 64 | browse menus and retrieve menu items | High / Medium / Low | | |
| # 65 | create and update restaurant information | High / Medium / Low | | |

### Customer Accounts

| User Story | Description | Priority | Primary Owner | Dependencies |
|---|---|---|---|---|
| # 66 | register a customer | High / Medium / Low | | |
| # 67 | sign in using the authentication mechanism required by the project | High / Medium / Low | | |
| # 68 | retrieve customer information | High / Medium / Low | | |
| # 69 | update customer information and delivery address | High / Medium / Low | | |
| # 70 | deactivate a customer account | High / Medium / Low | | |

### Authentication and Authorization

| User Story | Description | Priority | Primary Owner | Dependencies |
|---|---|---|---|---|
| # 71 | the backend identifies authenticated users | High / Medium / Low | | |
| # 72 | the backend enforces role-restricted operations | High / Medium / Low | | |
| # 73 | unauthenticated and unauthorized requests return appropriate API responses | High / Medium / Low | | |
| # 74 | the team can explain where authentication and authorization decisions are enforced | High / Medium / Low | | possibly one way hash function with information and checking corrected api-endpoint |

### Shopping Cart

| User Story | Description | Priority | Primary Owner | Dependencies |
|---|---|---|---|---|
| # 75 | create or retrieve the active cart for a customer | High / Medium / Low | | |
| # 76 | add menu items | High / Medium / Low | | |
| # 77 | update item quantities | High / Medium / Low | | |
| # 78 | remove menu items | High / Medium / Low | | |
| # 79 | clear the cart | High / Medium / Low | | |
| # 80 | retrieve current cart contents | High / Medium / Low | | |
| # 81 | retrieve authoritative subtotal and total values calculated by the backend | High / Medium / Low | | |

### Checkout and Order Creation

| User Story | Description | Priority | Primary Owner | Dependencies |
|---|---|---|---|---|
| # 82 | Validate current customer, restaurant, cart, menu items, quantities, and required business rules. | High / Medium / Low | | |
| # 83 | Recalculate prices and the authoritative total using current data. | High / Medium / Low | | |
| # 84 | Create an order containing the information required to represent the transaction. | High / Medium / Low | | |
| # 85 | Persist the order. | High / Medium / Low | | |
| # 86 | Clear or close the active cart only after successfully saving the order. | High / Medium / Low | | |
| # 87 | Return or retrieve the created order. | High / Medium / Low | | |

### Orders

| User Story | Description | Priority | Primary Owner | Dependencies |
|---|---|---|---|---|
| # 88 | retrieve an individual order; | High / Medium / Low | | |
| # 89 | retrieve orders associated with a customer | High / Medium / Low | | |
| # 90 | preserve the initial information required for later historical-order integrity | High / Medium / Low | | |

>this is a draft sprint plan. The team will finalize the sprint backlog after the planning meeting.

> **Important:** Primary ownership means that the student is responsible for coordinating the work. It does not mean that the student works alone or that other team members cannot contribute.

---

## 3. Task Decomposition

Break larger user stories into smaller tasks that can be implemented, reviewed, and tested.

### User Story #[NUMBER] — [TITLE]

- [#62] As a customer, I want to discover, search, and filter restaurants so that I can find a restaurant that meets my needs.
- [#63] As a customer, I want to retrieve restaurant details so that I can learn more about a restaurant before deciding to order from it.
- [#64] As a customer, I want to add menu items to my cart so that I can purchase them later.

- [#65] As a restaurant owner, I want to create and update restaurant information so that I can manage my restaurant's presence on the platform.
- [#66] As a customer, I want to register an account so that I can place orders and manage my information.
- [#67] As a customer, I want to sign in using the authentication mechanism required by the project so that I can access my account and place orders.
- [#68] As a customer, I want to retrieve my information so that I can view and manage my account details.
- [#69] As a customer, I want to update my information and delivery address so that I can ensure my orders are delivered correctly.
- [#70] As a customer, I want to deactivate my account so that I can remove my presence from the platform.
- [#71] As a backend system, I want to identify authenticated users so that I can enforce access control and security.
- [#72] As a backend system, I want to enforce role-restricted operations so that I can ensure that only authorized users can perform certain actions.
- [#73] As a backend system, I want unauthenticated and unauthorized requests to return appropriate API responses so that I can provide clear feedback to clients and maintain security.
- [#74] As a team, we want to explain where authentication and authorization decisions are enforced so that we can demonstrate our understanding of security best practices.
- [#75] As a customer, I want to create or retrieve the active cart so that I can manage my selected items before placing an order.
- [#76] As a customer, I want to add menu items to my cart so  that I can purchase them later.
- [#77] As a customer, I want to update item quantities in my cart so that I can adjust my order before checkout.
- [#78] As a customer, I want to remove menu items from my cart so I could select what I do not want
- [#79] As a customer, I want to clear items in my cart so I do not need to repeatly remove items from my cart
- [#80] As backend system, I need to retrieve current cart contents so that I could calculate further details like total price
- [#81] As backend system, I need to retrieve authoritative subtotal and total values calculated by the backend so I could provide to customer their items total price

- [#82] As a backend system, I want to validate the customer, restaurant, cart, menu items, quantities and business rules before checkout so that only valid orders are created.
- [#83] As a backend system, I want to recalculate prices and the authoritative total from current data so that stale cart prices are not used.
- [#84] As a backend system, I want to create an order containing the information required to represent the transaction so that the purchase is recorded.
- [#85] As a backend system, I want to persist the order so that it survives a restart.
- [#86] As a backend system, I want to clear or close the active cart only after the order is successfully saved so that no order is lost.
- [#87] As a customer, I want to see the created order so that I know my purchase succeeded.
- [#88] As a customer, I want to retrieve an individual order so that I can review it.
- [#89] As a customer, I want to retrieve the orders associated with my account so that I can see my order history.
- [#90] As a backend system, I want to preserve the order's initial information so that later menu or price changes do not alter historical orders.

- [ ] Documentation / API updates

---

## 4. Dependencies and Integration

Identify work that depends on another team member, subsystem, or component.

| Dependency | Related User Stories | Who is Responsible? | Planned Resolution |
|---|---|---|---|
| Cart needs an authenticated customer identity | #75 depends on #66, #71 | | Agree the "current user" interface before Cart work begins so Cart can be built against it |
| Cart needs menu item lookup and availability | #76 depends on #64 | | Menu owner exposes a service function that Cart calls; Cart does not read menu data directly |
| Cart needs restaurant identity | #76, one-restaurant-per-cart rule | | Complete restaurant validation first so Cart can rely on it |
| Checkout needs a complete, valid cart | #82–#87 depend on #75–#81 | | Cart owner confirms the cart service interface is stable before Checkout starts |
| Checkout must re-read current menu prices | #83 depends on #64 | | Checkout calls the menu service rather than trusting values stored in the cart |
| Order retrieval needs persisted orders | #88–#90 depend on #85 | | Build order retrieval after order creation is merged |
| Everyone edits shared data files and schemas | All stories | | Agree on file names, id fields and schema field names at the lab before coding |

### Integration Plan

<!-- Describe how the team will integrate the work during the sprint. -->

The critical path is:

```
Auth (#71–#73) → Customer (#66–#70) → Cart (#75–#81) → Checkout (#82–#87) → Orders (#88–#90)
```
> possible endpoint check for authentication and authorization, the draft workflow will be like this


Menu (#64) feeds into both Cart and Checkout.

1. Service function names, schema
   field names and data file names are settled at the lab, written down, and not
   changed without telling the team.
2. Whoever owns authentication lands a working "identify the
   current user" mechanism early, even if role enforcement follows later, so
   that Cart and Checkout are not blocked.
3. No subsystem reads
   another subsystem's data file directly, and no data is duplicated or
   hard-coded to make an endpoint work on its own.
4. Merge each slice as soon as it
   works rather than keeping long-lived branches.
5. CI runs on every push and pull request, and the check must pass before a
   pull request is merged.
6. Integrate continuously, not at the end. As soon as Cart works, write the
   Customer → Menu → Cart test. As soon as Checkout works, extend it through to
   Order. The full-path test should exist before the final week.


---


## 5. Risks and Potential Blockers

Identify anything that could prevent the team from achieving the sprint goal.

| Risk / Blocker | Impact | Planned Action | Owner |
|---|---|---|---|
| Uneven task sizes or unclear ownership | Some members may have too much work or wait for others. | Compare effort and dependencies when assigning functions after Friday's lab. | All team members |
| Different names or overlapping edits | Integration errors and merge conflicts. | Agree on names and interfaces early; coordinate changes to shared files. | All team members |
| Missing AI records or weak presentation preparation | Incomplete documentation or difficulty explaining the work. | Record AI assistance as work is done and rehearse the lab presentation. | Each contributor |
| Authentication is on the critical path | Cart, Checkout and Orders all stall if it is late. | Start authentication first; land user identification early even if roles follow later. | Auth owner |
| Subsystems built in isolation and integrated late | The demo requires the connected workflow, not separate endpoints. | Write the cross-subsystem test as soon as each link exists. | All team members |

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
| Lucas Liu | Prepare for the lab and help agree on names and workflow; detailed functions pending. | ☐ |
| Allan Zhang | Prepare for the lab; expressed interest in menu item functions; final scope pending. | ☐ |
| Xingyu Tang | Prepare for the lab and help agree on names and workflow; detailed functions pending. | ☐ |
| Jingyuan Peng | Prepare for the lab and help agree on names and workflow; detailed functions pending. | ☐ |

---

## Meeting Notes

<!-- Add any additional notes, decisions, or questions from the planning meeting. -->