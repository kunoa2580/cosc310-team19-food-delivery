# Sprint Planning M1

## Sprint Information

- **Sprint / Milestone:** Milestone 1 (M1)
- **Sprint dates:** To be confirmed after Friday's lab.
- **Planning meeting date:** 2026-09-30, 7:30 p.m.
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

Complete the M1 workflow from the frontend through the backend to saved data and back. Build and check the backend first, then connect the frontend. Share work more evenly by assigning each person one or a few functions and the related work across the four backend layers.

---

## 2. Sprint Backlog

Select the user stories that the team commits to working on during this sprint.

| User Story | Description | Priority | Primary Owner | Dependencies |
|---|---|---|---|---|
| #1 | Complete the backend functions needed for the M1 workflow, including menu items. | High | To be confirmed; Allan expressed interest in menu items. | Review M1 requirements and agree on names and interfaces. |
| #2 | Connect the frontend to the working backend and demonstrate the complete M1 workflow. | High | To be confirmed after Friday's lab. | Backend functions and API responses are ready. |
| #3 | Prepare for Friday's lab presentation and questions. | High | All team members | Review the current code, tests, and project plan. |
| #4 | Agree on function ownership, naming, GitHub workflow, and AI documentation. | High | All team members | Friday's lab feedback before final task assignments. |

> **Important:** Primary ownership means that the student is responsible for coordinating the work. It does not mean that the student works alone or that other team members cannot contribute.

---

## 3. Task Decomposition

Break larger user stories into smaller tasks that can be implemented, reviewed, and tested.

### User Story #1 — Complete the M1 Backend

- [ ] Check the M1 to-do list against the milestone requirements.
- [ ] Agree on function names, variable names, inputs, and outputs before coding.
- [ ] Confirm which menu item functions Allan will take on after Friday's lab.
- [ ] Implement each assigned function through the related routes, services, repositories, and persistence.
- [ ] Tests: Check business rules, API behavior, and saved data after restarting.
- [ ] Documentation / API updates: Update API details and record AI assistance in `docs/PROVENANCE.md`.

### User Story #2 — Connect the Frontend

- [ ] Start frontend integration after the required backend functions work.
- [ ] Connect the M1 interface to the agreed API endpoints.
- [ ] Show results and errors clearly in the interface.
- [ ] Tests: Check the full workflow from the interface to saved data and back.
- [ ] Documentation / API updates: Update instructions for running and demonstrating the workflow.

### User Story #3 — Prepare for Friday's Lab

- [ ] Practice running the application and showing the current working features.
- [ ] Make sure everyone can explain the layers, tests, and their own contributions.
- [ ] Tests: Run the current test suite before the presentation.

### User Story #4 — Organize Team Development

- [ ] After Friday's lab, divide the detailed tasks based on effort and dependencies.
- [ ] Assign each person one or a few functions with the related work across the four backend layers.
- [ ] Write down agreed function and variable names before implementation.
- [ ] Coordinate edits to shared files to reduce merge conflicts.
- [ ] Tests: Include relevant tests with each function's pull request.
- [ ] Documentation / API updates: Keep the GitHub Project Board and `docs/PROVENANCE.md` updated.

---

## 4. Dependencies and Integration

Identify work that depends on another team member, subsystem, or component.

| Dependency | Related User Stories | Who is Responsible? | Planned Resolution |
|---|---|---|---|
| Shared function names, variable names, and data formats | #1, #2, #4 | All team members | Agree on names, inputs, and outputs before coding. |
| Frontend needs working backend functions | #1, #2 | Function owners, to be confirmed | Build and test the backend first, then connect the frontend. |
| Final task assignments depend on Friday's lab feedback | #1, #2, #4 | All team members | Confirm detailed assignments after the lab on 2026-10-02. |

### Integration Plan

Use an issue and a feature branch for each assigned function or small related set of functions. Each owner implements the related work across the four backend layers, adds tests, and opens a pull request. Another teammate reviews it before merging into the team's working version. Coordinate shared-file edits and test the complete workflow after integration.

The project overview PDF specifically requires feature branches and pull requests, no direct implementation commits to `main`, no self-approval of pull requests, teammate review of significant changes, and test evidence for important pull requests.

---

## 5. Risks and Potential Blockers

Identify anything that could prevent the team from achieving the sprint goal.

| Risk / Blocker | Impact | Planned Action | Owner |
|---|---|---|---|
| Uneven task sizes or unclear ownership | Some members may have too much work or wait for others. | Compare effort and dependencies when assigning functions after Friday's lab. | All team members |
| Different names or overlapping edits | Integration errors and merge conflicts. | Agree on names and interfaces early; coordinate changes to shared files. | All team members |
| Missing AI records or weak presentation preparation | Incomplete documentation or difficulty explaining the work. | Record AI assistance as work is done and rehearse the lab presentation. | Each contributor |

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

- The meeting started at 7:30 p.m. on 2026-09-30.
- We reviewed the M1 to-do list and discussed sharing work more evenly.
- We discussed how to prepare for Friday's lab presentation.
- We decided to prioritize the backend, then connect the frontend.
- We decided to agree on function and variable names before coding.
- Each person will implement one or a few functions and the related work across the four backend layers to reduce code conflicts.
- Allan noted that he would like to take care of menu item functions. The exact functions will be confirmed later.
- We will wait until after Friday's lab to finalize detailed task assignments.
- We agreed to pay more attention to recording AI assistance in `docs/PROVENANCE.md`.
- Section 13 of the project overview PDF specifically requires recording consequential external assistance, including code, tests, diagrams, design decisions, and documentation, using the milestone's required provenance labels. This includes AI assistance with this planning document.
- The numbers above are planning references; replace them with actual GitHub issue numbers when available.
- Sprint dates, facilitator, attendance, and individual confirmations still need to be recorded.
