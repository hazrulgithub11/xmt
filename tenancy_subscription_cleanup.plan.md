# Tenancy + Subscription Cleanup Plan

Status: `In Progress`  
Owner: `Billing Team`  
Last Updated: `2026-06-03`

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

## Phase-By-Phase Execution Plan

## Phase 0 - Baseline and Safety Net
Status: `TODO`

Goal:
- Freeze current behavior and make cleanup trackable.

Files to change + manager reason:
- `tenancy_subscription_cleanup.plan.md`  
  Reason: Create a single progress tracker with scope, sequencing, and accountability.
- `xmt.plan.md` (optional summary link only)  
  Reason: Keep one-line pointer to active cleanup tracker for team visibility.

Acceptance:
- Plan approved.
- Team aligns on "no behavior change" baseline before refactor.

---

## Phase 1 - Workflow Consolidation (Duplicate Workflow)
Status: `TODO`

Goal:
- Keep exactly one active orchestration path per scenario.

Files to change + manager reason:
- `application/forms/Subscription/workflow/Handle_Subscription_Submi.deluge`  
  Reason: Keep as primary add/edit billing orchestration entry.
- `application/forms/Subscription/workflow/Handle_Creation_Of_Subscr.deluge`  
  Reason: Mark as legacy/deprecated path to prevent dual maintenance confusion.
- `application/forms/Subscription/workflow/Handle_Edit_Submission.deluge`  
  Reason: Mark as legacy/deprecated path to avoid duplicate execution logic.
- `application/Schedule/Handle_Creation_Of_Subscr1.deluge`  
  Reason: Normalize monthly schedule call path.
- `application/Schedule/Handle_Creation_Of_Invoic.deluge`  
  Reason: Normalize non-monthly schedule call path.

Acceptance:
- One clear orchestration path for add/edit.
- Schedules call normalized entry functions only.

---

## Phase 2 - Centralize Billing-Date Calculations (Duplicated Calculation)
Status: `TODO`

Goal:
- Move repeated billing date computations into one shared utility layer.

Files to change + manager reason:
- `application/Custom Functions/tenancy/convert_bill_cycle_to_int`  
  Reason: Add safe default + validation to avoid null/undefined downstream behavior.
- `application/Custom Functions/tenancy/fetch_subscription_and_tenancy_details`  
  Reason: Reduce inline date logic and route to centralized date utility.
- `application/Custom Functions/subscription/update_subscription_next_and_last_billing_date`  
  Reason: Make this the authoritative updater for next/latest/final date transitions.
- `application/forms/Subscription/workflow/Handle_Subscription_Submi.deluge`  
  Reason: Replace repeated date math blocks with shared function calls.
- `application/forms/Subscription/workflow/Handle_Contract_Start_Dat.deluge`  
  Reason: Remove duplicated billing-date derivation from user-input workflow.
- `application/forms/Subscription/workflow/Handle_Contract_End_Date_.deluge`  
  Reason: Remove duplicated billing-date derivation from user-input workflow.

Acceptance:
- Billing-date formulas are defined once and reused.
- Start/end date user-input workflows only do UI/validation responsibilities.

---

## Phase 3 - Centralize Amount + Proration Calculations (Duplicated Calculation)
Status: `TODO`

Goal:
- Unify line amount, proration, and quantity behavior across invoice variants.

Files to change + manager reason:
- `application/Custom Functions/invoice/create_invoice_current_monthly`
- `application/Custom Functions/invoice/create_invoice_previous_monthly`
- `application/Custom Functions/invoice/create_invoice_current_not_monthly`
- `application/Custom Functions/invoice/create_invoice_previous_not_monthly`
- `application/Custom Functions/invoice/create_invoice` (legacy compatibility path)
  Reason (all above): consolidate repeated math blocks into shared helpers and remove drift between paths.

Acceptance:
- One formula policy for proration and quantity.
- Consistent totals regardless of monthly/non-monthly path.

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

- [ ] Phase 0 - Baseline and Safety Net
- [ ] Phase 1 - Workflow Consolidation
- [ ] Phase 2 - Centralize Billing-Date Calculations
- [ ] Phase 3 - Centralize Amount + Proration Calculations
- [ ] Phase 4 - Fix Wrong Logic Calculations
- [ ] Phase 5 - Ticket Workflow Unification
- [ ] Phase 6 - Tenancy Guardrails + Data Integrity

---

## Change Log (Manager Update Format)

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
