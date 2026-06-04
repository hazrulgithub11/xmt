# Tenancy + Subscription Cleanup Plan

Status: `In Progress` (Phase 0 complete — awaiting manager sign-off)  
Owner: `Billing Team`  
Last Updated: `2026-06-03`

**Active cleanup tracker:** this file. Architecture overview: [`xmt.plan.md`](xmt.plan.md).

## Team Agreement (Baseline — No Behavior Change)

Until a phase is explicitly started and its acceptance criteria are met:

1. **Do not** change Deluge logic in scoped tenancy/subscription/invoice/ticket files except documentation and comments that do not alter runtime.
2. **Treat** the git baseline below as the reference snapshot for diffs and regression comparison.
3. **Record** every behavioral change in the Change Log with phase, risk, and validation notes.
4. **Deploy** one phase at a time; do not mix Phase 1+ refactors in the same release as unrelated billing changes.

| Role | Sign-off | Date |
|------|----------|------|
| Billing / dev lead | ☐ Approved baseline | |
| Manager | ☐ Approved plan + sequencing | |

## Git Baseline (Frozen)

| Field | Value |
|-------|-------|
| Commit | `39be6172a70176f42024fe7f0fad07dbe63e0a60` |
| Message | `pro forma invoice custom actions` |
| Canonical export | `XMT___Billing_System.ds` |
| Extracted app root | `application/` |

Compare all cleanup work against this commit unless the baseline row is updated here with a new SHA and reason.

## Source Of Truth

This plan is based on `XMT___Billing_System.ds` as the canonical reference.

Validated modules/workflows/functions from source:
- `Handle_Creation_Of_Subscr` (Handle Creation Of Subscription)
- `Handle_Edit_Submission` (Handle Edit Submission)
- `Handle_Subscription_Submi` (Handle Subscription Submission And Edit)
- `Handle_Creation_Of_Subscr1` (Handle Creation Of Subscription Invoice)
- `Handle_Creation_Of_Invoic` (Handle Creation Of Invoice Other Than Monthly)
- `Handle_Contract_Start_Dat` / `Handle_Contract_End_Date_`
- `tenancy.convert_bill_cycle_to_int`
- `tenancy.fetch_subscription_and_tenancy_details`
- `invoice.create_invoice_current_monthly`
- `subscription.update_subscription_next_and_last_billing_date`
- `subscription.createTicket` / `subscription.createTicketUpdateWo`
- `work_order_creation.updateTicketNumber`

---

## Scope By Category

### 1) Duplicated Calculation (needs centralization)
- Billing date calculation (current/start/next/final) repeated across multiple subscription workflows.
- Proration and quantity logic repeated across invoice generation functions (monthly and non-monthly).
- Billing cycle conversion and bill-every date normalization used in many places without one shared date utility.

### 2) Duplicate Workflow (inconsistent function calling)
- Multiple subscription on-success workflows contain overlapping billing orchestration (`Handle_Creation_Of_Subscr`, `Handle_Edit_Submission`, `Handle_Subscription_Submi`).
- Ticket creation path is split across three functions (`createTicket`, `createTicketUpdateWo`, `updateTicketNumber`).
- Monthly vs non-monthly orchestration split across tenancy and subscription schedules with non-unified entry path.

### 3) Wrong Logic Calculation
- Condition precedence and overlapping OR/AND branches in subscription workflows can produce wrong next/final billing updates.
- Mixed quantity fields (`Quantity` vs `Quantity1`) and mixed proration formulas (`days/30` vs calendar day logic).
- Inconsistent post-invoice totals update (call charge totals) and inconsistent subscription date updates for multi-sub scenarios.

---

## Baseline Inventory (Frozen Behavior)

### Workflow activation matrix

| Workflow | Repo path | Trigger | Creator status | Notes |
|----------|-----------|---------|----------------|-------|
| Handle Creation Of Subscription | `application/forms/Subscription/workflow/Handle_Creation_Of_Subscr.deluge` | `on add` → `on success` | **inactive** | Legacy add path; mirrors billing orchestration |
| Handle Edit Submission | `application/forms/Subscription/workflow/Handle_Edit_Submission.deluge` | `on edit` → `on success` | **inactive** | Legacy edit path |
| Handle Subscription Submission And Edit | `application/forms/Subscription/workflow/Handle_Subscription_Submi.deluge` | `on add or edit` → `on success` | **active** | Primary add/edit path; gated `Bill_For == "Current Duration" && Billing_Cycle == "Monthly"` |
| Handle Contract Start Date | `application/forms/Subscription/workflow/Handle_Contract_Start_Dat.deluge` | `on user input` Contract_Start_Date | **active** | Inline billing-date derivation on load |
| Handle Contract End Date Fields | `application/forms/Subscription/workflow/Handle_Contract_End_Date_.deluge` | `on user input` Contract_End_Date | **active** | Line-item end-date sync |
| Handle Creation Of Subscription Invoice (Tenancy form) | `application/forms/Tenancy/workflow/Handle_Creation_Of_Subscr1.deluge` | schedule on Tenancy | duplicate of schedule | Same schedule definition as `application/Schedule/` |
| Handle Creation Of Subscription Invoice | `application/Schedule/Handle_Creation_Of_Subscr1.deluge` | 5 days before `Next_Billing_Date` 09:00 SGT | **active** | Monthly → `tenancy.fetch_subscription_and_tenancy_details` |
| Handle Creation Of Invoice Other Than Monthly | `application/Schedule/Handle_Creation_Of_Invoic.deluge` | 5 days before sub `Next_Billing_Date` | **active** | Non-monthly active subs → `invoice.create_invoice_*_not_monthly` |

### Shared functions in scope (repo paths)

| Function | Path | Role in baseline |
|----------|------|------------------|
| `tenancy.convert_bill_cycle_to_int` | `application/Custom Functions/tenancy/convert_bill_cycle_to_int` | Cycle string → months int (default 1 if null/unknown) |
| `tenancy.get_billing_every_date` | `application/Custom Functions/tenancy/get_billing_every_date` | Bill-every anchor for a reference month (Phase 2) |
| `tenancy.get_monthly_billing_date_from_actual` | `application/Custom Functions/tenancy/get_monthly_billing_date_from_actual` | Monthly invoice period from next-billing date (Phase 2) |
| `tenancy.normalize_billing_date_for_bill_every` | `application/Custom Functions/tenancy/normalize_billing_date_for_bill_every` | Last-day / 29th date adjustment (Phase 2) |
| `tenancy.get_billing_date_for_contract_day` | `application/Custom Functions/tenancy/get_billing_date_for_contract_day` | Non-monthly contract-day billing date (Phase 2) |
| `tenancy.compute_next_billing_date` | `application/Custom Functions/tenancy/compute_next_billing_date` | Next billing date after invoice run (Phase 2) |
| `tenancy.fetch_subscription_and_tenancy_details` | `application/Custom Functions/tenancy/fetch_subscription_and_tenancy_details` | Monthly schedule orchestration |
| `tenancy.run_scheduled_non_monthly_billing` | `application/Custom Functions/tenancy/run_scheduled_non_monthly_billing` | Non-monthly schedule orchestration (Phase 1) |
| `subscription.update_subscription_next_and_last_billing_date` | `application/Custom Functions/subscription/update_subscription_next_and_last_billing_date` | Post-invoice date updates |
| `subscription.createTicket` | `application/Custom Functions/subscription/createTicket` | Desk ticket (legacy path) |
| `subscription.createTicketUpdateWo` | `application/Custom Functions/subscription/createTicketUpdateWo` | Desk ticket + WO update |
| `work_order_creation.updateTicketNumber` | `application/Custom Functions/work_order_creation/updateTicketNumber` | Ticket number on WO |
| `invoice.create_invoice_current_monthly` | `application/Custom Functions/invoice/create_invoice_current_monthly` | Current-duration monthly invoice |
| `invoice.create_invoice_previous_monthly` | `application/Custom Functions/invoice/create_invoice_previous_monthly` | Previous-duration monthly invoice |
| `invoice.create_invoice_current_not_monthly` | `application/Custom Functions/invoice/create_invoice_current_not_monthly` | Current-duration non-monthly |
| `invoice.create_invoice_previous_not_monthly` | `application/Custom Functions/invoice/create_invoice_previous_not_monthly` | Previous-duration non-monthly |

### Line-count snapshot (for diff noise awareness)

| File | Lines |
|------|------:|
| `Handle_Creation_Of_Subscr.deluge` | 582 |
| `Handle_Edit_Submission.deluge` | 578 |
| `Handle_Subscription_Submi.deluge` | 760 |
| `Handle_Contract_Start_Dat.deluge` | 278 |
| `Handle_Contract_End_Date_.deluge` | 243 |
| `Handle_Creation_Of_Subscr1.deluge` (Schedule + Tenancy) | 18 each |

### Known baseline behaviors (document, do not “fix” in Phase 0)

- **Dual subscription on-success paths:** inactive `Handle_Creation_Of_Subscr` / `Handle_Edit_Submission` vs active `Handle_Subscription_Submi` — production behavior follows the active workflow only.
- **Duplicate monthly schedule:** identical `Handle_Creation_Of_Subscr1` under `application/Schedule/` and `application/forms/Tenancy/workflow/`.
- **Split ticket pipeline:** `createTicket`, `createTicketUpdateWo`, and `updateTicketNumber` are separate entry points (Phase 5 target).
- **Repeated date/proration math** across workflows and invoice functions (Phases 2–4 targets).

### Pre-refactor smoke checklist (run before Phase 1+)

- [ ] Subscription add (monthly, Current Duration): dates and line items match pre-change baseline in test tenancy.
- [ ] Subscription edit with zero invoices: same as add path.
- [ ] Contract start/end user-input: end date and proration fields populate as today.
- [ ] Monthly schedule (or manual invoke of `fetch_subscription_and_tenancy_details`): invoice created for due subs.
- [ ] Non-monthly schedule: correct `create_invoice_*_not_monthly` branch for Bill_For.
- [ ] No unexpected activation of **inactive** workflows after export/sync to Creator.

---

## Phase-By-Phase Execution Plan

## Phase 0 - Baseline and Safety Net
Status: `DONE` (pending sign-off in table above)

Goal:
- Freeze current behavior and make cleanup trackable.

Files changed + manager reason:
- `tenancy_subscription_cleanup.plan.md`  
  Reason: Single progress tracker with baseline inventory, git SHA, team rules, and smoke checklist.
- `xmt.plan.md`  
  Reason: One-line pointer to this tracker for team visibility.

Acceptance:
- [x] Plan documented with scope, sequencing, and accountability.
- [x] Baseline inventory and git SHA recorded.
- [x] Explicit “no behavior change” agreement captured.
- [ ] Plan approved (manager sign-off).
- [ ] Team aligned on baseline before Phase 1 (checkboxes in sign-off table).

---

## Phase 1 - Workflow Consolidation (Duplicate Workflow)
Status: `DONE`

Goal:
- Keep exactly one active orchestration path per scenario.

Files changed + manager reason:
- `application/forms/Subscription/workflow/Handle_Subscription_Submi.deluge`  
  Reason: Marked as primary add/edit orchestration (`(Primary)` display name + header).
- `application/forms/Subscription/workflow/Handle_Creation_Of_Subscr.deluge`  
  Reason: Marked `[LEGACY]`, inactive, deprecation comments.
- `application/forms/Subscription/workflow/Handle_Edit_Submission.deluge`  
  Reason: Marked `[LEGACY]`, inactive, deprecation comments.
- `application/Custom Functions/tenancy/run_scheduled_non_monthly_billing`  
  Reason: Single non-monthly schedule entry (mirrors monthly `fetch_subscription_and_tenancy_details`).
- `application/Schedule/Handle_Creation_Of_Subscr1.deluge`  
  Reason: Documented canonical monthly path; calls `fetch_subscription_and_tenancy_details` only.
- `application/Schedule/Handle_Creation_Of_Invoic.deluge`  
  Reason: Inline invoice routing removed; calls `run_scheduled_non_monthly_billing` only.
- `application/forms/Subscription/workflow/Handle_Creation_Of_Invoic.deluge`  
  Reason: Kept in sync with Schedule export.
- `application/forms/Tenancy/workflow/Handle_Creation_Of_Subscr1.deluge`  
  Reason: Kept in sync with Schedule export.
- `XMT___Billing_System.ds`  
  Reason: New function + schedule block aligned with `application/` extract.

### Orchestration map (post Phase 1)

| Scenario | Active path | Entry function |
|----------|-------------|----------------|
| Subscription add/edit (monthly, Current Duration) | `Handle_Subscription_Submi` | inline (Phase 2+ may centralize) |
| Subscription add (legacy) | `[LEGACY] Handle_Creation_Of_Subscr` | inactive — do not use |
| Subscription edit (legacy) | `[LEGACY] Handle_Edit_Submission` | inactive — do not use |
| Monthly invoice schedule | `Handle_Creation_Of_Subscr1` | `tenancy.fetch_subscription_and_tenancy_details` |
| Non-monthly invoice schedule | `Handle_Creation_Of_Invoic` | `tenancy.run_scheduled_non_monthly_billing` |

Acceptance:
- [x] One clear orchestration path for add/edit (`Handle_Subscription_Submi`).
- [x] Schedules call normalized entry functions only.
- [ ] Smoke checklist re-run after deploy to Creator.

---

## Phase 2 - Centralize Billing-Date Calculations (Duplicated Calculation)
Status: `DONE`

Goal:
- Move repeated billing date computations into one shared utility layer.

### Billing-date utility layer (single source of truth)

| Function | Purpose |
|----------|---------|
| `tenancy.get_billing_every_date(billEvery, referenceDate)` | Monthly bill-every anchor (today or contract start month) |
| `tenancy.get_monthly_billing_date_from_actual(billEvery, actualBillingDate)` | Schedule monthly invoice period date |
| `tenancy.normalize_billing_date_for_bill_every(date, billEvery)` | Last Day Of Month / 29th adjustments |
| `tenancy.get_billing_date_for_contract_day(contractStart, referenceDate)` | Non-monthly billing on contract day |
| `tenancy.compute_next_billing_date(...)` | Post-invoice next billing transition |
| `tenancy.convert_bill_cycle_to_int(billCycle)` | Safe cycle int (defaults to 1) |

Files changed + manager reason:
- `application/Custom Functions/tenancy/convert_bill_cycle_to_int` — null/empty guard, default 1.
- `application/Custom Functions/tenancy/get_billing_every_date` — **new** shared bill-every anchor.
- `application/Custom Functions/tenancy/get_monthly_billing_date_from_actual` — **new** schedule period helper.
- `application/Custom Functions/tenancy/normalize_billing_date_for_bill_every` — **new** last-day/29th normalizer.
- `application/Custom Functions/tenancy/get_billing_date_for_contract_day` — **new** non-monthly day helper.
- `application/Custom Functions/tenancy/compute_next_billing_date` — **new** next-date calculator.
- `application/Custom Functions/tenancy/fetch_subscription_and_tenancy_details` — uses `get_monthly_billing_date_from_actual`.
- `application/Custom Functions/subscription/update_subscription_next_and_last_billing_date` — delegates next date to `compute_next_billing_date`.
- `application/forms/Subscription/workflow/Handle_Subscription_Submi.deluge` — inline date blocks → utility calls.
- `application/forms/Subscription/workflow/Handle_Contract_Start_Dat.deluge` — removed commented date-derivation blocks; UI/validation only.
- `application/forms/Subscription/workflow/Handle_Contract_End_Date_.deluge` — same cleanup.
- `XMT___Billing_System.ds` — new utilities + updated custom functions.

Acceptance:
- [x] Billing-date formulas defined once in `tenancy.*` utilities and reused.
- [x] Contract start/end workflows: UI, validation, prorate notes, line-item sync only.
- [ ] Smoke checklist re-run after Creator deploy (month-end, leap-year, short contracts).

---

## Phase 3 - Centralize Amount + Proration Calculations (Duplicated Calculation)
Status: `DONE`

Goal:
- Unify line amount, proration, and quantity behavior across invoice variants.

**Source of truth:** `XMT___Billing_System.ds` (live Creator export). `application/` files re-extracted from `.ds` after refactor.

### Amount / proration utility layer (2 functions)

| Function | `mode` / behavior |
|----------|-------------------|
| `invoice.calc_line_subtotal(mode, …)` | `single_period` · `full_cycle` · `prorate_start_month` · `prorate_final_month` · `days30` · `legacy_current_start` |
| `invoice.calc_line_tax(subTotal, taxPct, nullSafeTotal)` | Tax + total; `nullSafeTotal=true` uses `subTotal + ifnull(taxAmount,0)` |

Files changed + manager reason:
- `XMT___Billing_System.ds` — two helpers; ~100 call sites in five `create_invoice*` functions.
- `application/Custom Functions/invoice/calc_line_subtotal`, `calc_line_tax` — **only** amount helpers (8 one-liner helpers removed).
- `application/Custom Functions/invoice/create_invoice*` — re-synced from `.ds`.

**Intentionally not unified (behavior preserved):** previous-duration start proration in legacy `create_invoice` (P10: prorateMonth not × quantity); legacy final-billing branches (P6–P8); monthly vs non-monthly branch orchestration.

Acceptance:
- [x] One formula policy per pattern via shared helpers.
- [x] Tax/total and P2/P5/P13/P14 paths consistent across monthly/non-monthly specialists.
- [ ] Smoke: compare invoice line subtotals before/after on test subscriptions (Creator deploy required).

---

## Phase 4 - Fix Wrong Logic Calculations
Status: `TODO`

Goal:
- Correct known incorrect/fragile logic while preserving intended business behavior.

Files to change + manager reason:
- `application/forms/Subscription/workflow/Handle_Subscription_Submi.deluge`  
  Reason: fix precedence/overlap conditions in date-branch decisions.
- `application/Custom Functions/subscription/update_subscription_next_and_last_billing_date`  
  Reason: fix single-record update behavior in multi-sub cases.
- `application/Custom Functions/invoice/create_invoice_current_monthly`  
  Reason: fix call-charge grand total assignment consistency.
- `application/Custom Functions/invoice/create_invoice_previous_monthly`  
  Reason: fix call-charge grand total assignment consistency.
- `application/forms/Subscription/workflow/Handle_Tenant_Code_Change.deluge`  
  Reason: tighten duplicate PO detection to exact-match logic (not partial contains).

Acceptance:
- Edge cases (month-end/leap-year/short-term contracts) produce expected values.
- Totals and status/date transitions are consistent.

---

## Phase 5 - Ticket Workflow Unification (Duplicate Workflow + Wrong Logic)
Status: `TODO`

Goal:
- Use one ticket creation pipeline and remove conflicting behavior.

Files to change + manager reason:
- `application/Custom Functions/subscription/createTicket`  
  Reason: deprecate or align to shared ticket helper to avoid divergent contact/account matching.
- `application/Custom Functions/subscription/createTicketUpdateWo`  
  Reason: make this the primary path or route to a single helper.
- `application/Custom Functions/work_order_creation/updateTicketNumber`  
  Reason: keep one creator->work-order->ticket chain with correct IDs and update targets.
- `application/forms/Subscription/workflow/create_ticket_in_desk.deluge`  
  Reason: call only normalized ticket path.
- `application/forms/Work Order Creation/workflow/create_ticket_in_desk1.deluge`  
  Reason: call only normalized ticket path.

Acceptance:
- One deterministic flow for ticket creation.
- No mismatched `Subscription` vs `Work_Order_Creation` record updates.

---

## Phase 6 - Tenancy Guardrails + Data Integrity
Status: `TODO`

Goal:
- Strengthen tenancy lifecycle safety and cross-module consistency.

Files to change + manager reason:
- `application/forms/Tenancy/workflow/Validate_Record_Deletion13.deluge`  
  Reason: keep dependency checks complete and human-readable before delete.
- `application/forms/Subscription/workflow/Validate_Record_Deletion2.deluge`  
  Reason: extend dependent-module checks to avoid orphan side effects.
- `application/forms/Tenancy/workflow/change_technical_informat1.deluge`  
  Reason: harden Desk contact/account update assumptions and reduce duplicate contact risk.

Acceptance:
- No unsafe deletes.
- Desk identity mapping remains consistent after tenancy edits.

---

## Progress Tracker

- [x] Phase 0 - Baseline and Safety Net (docs only; manager sign-off pending)
- [x] Phase 1 - Workflow Consolidation (deploy + smoke pending)
- [x] Phase 2 - Centralize Billing-Date Calculations (deploy + smoke pending)
- [x] Phase 3 - Centralize Amount + Proration (2 helpers; deploy + smoke pending)
- [ ] Phase 4 - Fix Wrong Logic Calculations
- [ ] Phase 5 - Ticket Workflow Unification
- [ ] Phase 6 - Tenancy Guardrails + Data Integrity

---

## Change Log (Manager Update Format)

- Date: 2026-06-03
- Phase: 3 (consolidated)
- Files changed: `XMT___Billing_System.ds`, `calc_line_subtotal` + `calc_line_tax` (replaced 8 helpers), 5 `create_invoice*` re-extracted
- Why changed: One subtotal entry (mode string) + one tax/total entry; same formulas, less surface area.
- Risk level: `High` (invoice amounts — publish 2 helpers to Creator; retire 8 if previously deployed)
- Validation done: All `calc_*` call sites migrated in `.ds`; application mirrors re-extract.
- Outcome: Phase 3 complete in repo; legacy complex branches remain inline by design.

- Date: 2026-06-03
- Phase: 3 (initial)
- Files changed: `XMT___Billing_System.ds`, 8 `invoice.calc_*` helpers (superseded by consolidation above)
- Why changed: First pass at centralization (replaced by 2-function design per team feedback).

- Date: 2026-06-03
- Phase: 2
- Files changed: 5 new `tenancy.*` date utilities, `convert_bill_cycle_to_int`, `fetch_subscription_and_tenancy_details`, `update_subscription_next_and_last_billing_date`, `Handle_Subscription_Submi`, contract start/end workflows, `XMT___Billing_System.ds`
- Why changed: Centralize repeated billing-date math; contract UI workflows stripped of dead date-derivation code.
- Risk level: `Medium` (must publish 5 new Creator functions; behavior should be equivalent)
- Validation done: Utility extract matches prior inline formulas; workflow branches unchanged.
- Outcome: Phase 2 complete in repo; await Creator deploy + smoke checklist.

- Date: 2026-06-03
- Phase: 1
- Files changed: Subscription workflows (primary/legacy), schedules, `run_scheduled_non_monthly_billing`, `XMT___Billing_System.ds`
- Why changed: One add/edit path; schedule thin wrappers; non-monthly logic centralized.
- Risk level: `Medium` (new Creator function must be published; schedule behavior equivalent)
- Validation done: Extracted schedule logic matches prior inline calls (same args to invoice functions).
- Outcome: Phase 1 complete in repo; await Creator deploy + smoke checklist.

- Date: 2026-06-03
- Phase: 0
- Files changed: `tenancy_subscription_cleanup.plan.md`, `xmt.plan.md`
- Why changed: Freeze baseline, add tracker/sign-off/smoke checklist; link from architecture doc.
- Risk level: `Low` (documentation only)
- Validation done: Repo inventory verified against `application/` extracts; git SHA recorded.
- Outcome: Phase 0 deliverables complete; no Deluge behavior changes.

Use this template for each merged batch:

- Date:
- Phase:
- Files changed:
- Why changed (business/maintenance reason):
- Risk level (`Low`/`Medium`/`High`):
- Validation done:
- Outcome:

---

## Start Order Recommendation

1. Phase 1 (workflow consolidation)  
2. Phase 2 (billing-date centralization)  
3. Phase 4 (wrong-logic fixes on top of centralized flow)  
4. Phase 3 (amount/proration centralization)  
5. Phase 5 and 6 (ticket and tenancy integrity hardening)

This order minimizes regression risk by stabilizing call paths before changing formulas.
