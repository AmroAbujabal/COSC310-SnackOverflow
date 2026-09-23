# SnackOverflow — Project Context for Claude Code

> Living document — I'll update this as the project moves through milestones. Treat it as
> current, but flag anything that looks out of date or contradicts what's actually in the repo.

## 1. What this is
SnackOverflow is a food-delivery application built for the COSC 310 (Software Engineering)
team term project at UBC Okanagan. Repo: AmroAbujabal/COSC310-SnackOverflow.

Team: Amr / Amro Ahmed (me), Al-Munther Bahanshal, Kenneth Tandianto.

The goal isn't just "an app that works" — the course grades on modularity, maintainability,
testability, reliability, documentation, reproducibility, and professional practice. Every
team member has to be able to individually explain requirements, architecture, business
rules, tests, and their own contributions. 40% of the grade is individual, based on
understanding and demonstrated contribution, not commit count or lines of code.

## 2. What we're building
Customers discover restaurants, browse menus, build a cart, place an order, and track it.
Restaurant users manage their own menu and incoming orders. Admins manage users/roles and
have system-wide oversight.

Five major workflows:
1. **Discover a restaurant** — list, search, filter by cuisine, view details
2. **Build a cart** — add/update/remove items, clear cart, calculate totals
3. **Place an order (checkout)** — validate current data, recalculate prices, create a
   complete order snapshot, save it, and only then close/clear the cart
4. **Manage an order and delivery** — progress orders through their lifecycle, cancel
   eligible orders, create deliveries, assign drivers, update delivery progress
5. **Manage the platform** — auth/roles, restaurant + menu management, reporting

Required functional areas: authentication & roles, restaurant discovery, menu management,
customer accounts, shopping cart, checkout & orders, order management, delivery
management, read-only reporting (restaurant revenue, most-ordered items, order counts by
status).

Optional features (only after required functionality is complete and stable): extra
search/filtering, favourites, ratings & reviews, promo codes/discounts, notifications,
enhanced delivery info.

Explicitly out of scope: real payment providers, real financial transactions, real GPS,
production-scale infrastructure, external delivery services. Orders simulate payment —
no real money moves.

## 3. Business rules that matter
- **The backend is authoritative.** A rule enforced only in the frontend doesn't count —
  a client can hit the API directly, so the backend must validate everything itself.
- **Authorization**: users can only perform operations their role permits.
- **Current-state validation**: check restaurants, menus, accounts, carts, orders, and
  deliveries against their actual current state before acting on them.
- **Historical integrity**: completed orders must preserve the data as it was at order
  time (price, items, etc.) — later menu/price changes must not retroactively alter a
  past order.

## 4. Required architecture (layered)
```
Frontend
   ↓
FastAPI Routes    — paths, params, requests/responses, status codes
   ↓
Service Layer     — business rules, calculations, validation, state transitions,
                     workflow orchestration
   ↓
Repository Layer  — storage operations, hides persistence details from services
   ↓
JSON / CSV Persistence
```
Keep these layers genuinely separate: routes shouldn't contain business logic, services
shouldn't touch storage/files directly.

## 5. Persistence
**JSON and/or CSV files — not a database.** Data must survive an app restart. Resources
need stable identifiers across restarts, and stored data must maintain valid relationships
(no orders referencing users/restaurants that don't exist). Automated tests must not
mutate the committed representative data — test isolation matters.

## 6. Tech stack
Python, FastAPI, Pydantic, pytest, Git & GitHub, JSON/CSV for storage. A Figma mockup from
the instructor is the UI spec/starting point (not a finished frontend) — the team is
responsible for the frontend, the backend, and the communication between them.

## 7. Testing
pytest-based automated testing throughout — a feature "working" in a manual demo isn't
enough, it needs tests. The suite must be reproducible by someone else following our docs.
Don't let tests touch committed test-fixture data.

## 8. GitHub workflow (required practices)
- No direct commits to `main`.
- Flow: Issue → feature branch → code + tests → PR → peer review → merge.
- Can't approve your own PR.
- Significant changes need review from another team member.
- Important PRs should include test evidence.
- The GitHub Project Board is the source of truth for who's doing what.
- Contribution is judged on quality, significance, consistency, and demonstrated
  understanding — not commit count or lines of code.

**PR descriptions**: always include one, short and human-sounding (not corporate
boilerplate) — what changed and why, in a couple sentences.

## 9. AI use & provenance — read before generating anything substantial
This project is governed by the course's Generative AI Use and Provenance Guide. Short
version: using AI is fine, but I stay responsible for understanding, validating, testing,
and explaining everything submitted.

- **The team maintains one shared file: `docs/PROVENANCE.md`.**
- Record AI use whenever AI affected something that's now part of the project — code,
  tests, docs, diagrams, API specs, or design decisions. Simple test: *did AI affect
  something now in our project? Yes → record it.* (Explaining a concept, decoding an
  error message, or trivial autocomplete doesn't need a record.)
- Each entry uses one of these labels:

  | Label | Use when... |
  |---|---|
  | **AI-GENERATED** | AI produced the content (or a substantial part) and I used/adapted it |
  | **AI-ASSISTED** | AI gave ideas/explanations/alternatives, but I wrote the final content myself |
  | **AI-REVISED** | I wrote it myself, and AI later substantially changed/refactored it |
  | **NO-AI** | No generative AI was involved |

- Each entry records: Student(s), Artifact, Provenance label, AI tool, Purpose,
  Influence, Validation, and PR/commit (when practical). If two students touch the same
  artifact using AI differently, each logs a separate entry.
- **When you (Claude Code) generate or substantially modify code, tests, docs, diagrams,
  or design decisions that I actually use, proactively draft the `docs/PROVENANCE.md`
  entry for it** (AI tool: Claude) so I just fill in Validation and the PR number instead
  of reconstructing it later.
- Not every commit needs a label — the provenance file is the record, linked to PRs/commits
  where practical.

## 10. Working style
- Explore the existing repo structure, README, and any docs before assuming layout — match
  existing conventions rather than inventing new ones.
- Make incremental, reviewable changes, not one giant commit.
- Briefly explain non-trivial design decisions (why this pattern, why this schema shape) —
  I need to be able to individually defend the work, not just submit it.
- Don't make architecture-level decisions unilaterally (storage shape, folder
  restructuring, cross-cutting patterns) — flag them for a team discussion first; per our
  team contract, decisions like that are made as a team or by majority vote, since
  Al-Munther and Kenneth also work in this repo.
- Write tests alongside a feature, not after.
- Use design patterns where they genuinely fit (e.g. repository pattern for storage,
  dependency injection via FastAPI's `Depends`) — don't force one in where it's not needed.

## 11. Current focus: M0 — Foundation
Establish the project structure and demonstrate that the major application and backend
layers are connected end-to-end (routes → service → repository → persistence), even with
minimal functionality. I'll update this section as we move into M1 (first vertical slice)
and beyond.
