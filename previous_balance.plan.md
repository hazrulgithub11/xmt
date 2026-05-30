# Previous Balance Standardization Plan

**Source of truth:** `XMT___Billing_System(1).ds` (latest live Zoho Creator export)

**Goal:** One calculation engine for `Previous_Balance` and `Total_Amount_Due`, called from every trigger — no duplicated inline loops.

**Repo root:** `application/`

**Status:** Rules confirmed — ready to implement.

---

## 1. Confirmed business rules ✅

Signed off by manager / product owner.

| # | Rule | Decision |
|---|------|----------|
| 1 | Date scope | **Invoice date order** — `Invoice_Date < current invoice date`. **Do not** use prior-month (`toStartOfMonth()`). |
| 2 | Unpaid filter | **Yes** — only include invoices where `Amount_Due > 0`. |
| 3 | Blueprint filter | **Yes** — only count invoices in `Blueprint.Current_Stage in {"Sent","Overdue","Partially Paid"}`. |
| 4 | Customer match | **`Customer` lookup ID** (same as current `invoice_balance_updates`). |
| 5 | Total formula | **`Total_Amount_Due = Amount_Due + Previous_Balance`** everywhere. |
| 6 | Miscellaneous charges | **Same rules** as all other invoices — no exemption. |
| 7 | Cascade scope | **`Invoice_Date > current invoice date`** (not `eomonth(0)`). |
| 8 | Payment received (add) | **Date-based** — replace live `Added_Time < zoho.currenttime` logic; re-enable cascade. |
| 9 | Debit notes | **TBD later** — out of scope for first implementation pass. |

### 1.1 Canonical calculation (single source of truth)

This is the **only** logic that should exist after migration:

```deluge
// invoice.invoice_balance_updates(invoice_id)
get_invoice = Invoice[ID == invoice_id];
invoice_date = get_invoice.Invoice_Date;
customer_id = get_invoice.Customer.ID;
current_amount_due = ifnull(get_invoice.Amount_Due, 0);

previous_balance_of_unpaid_invoices = 0;
if(invoice_date != null && customer_id != null)
{
    for each curr_invoice in Invoice[
        Amount_Due > 0
        && Blueprint.Current_Stage in {"Sent","Overdue","Partially Paid"}
        && Invoice_Date < invoice_date
        && Customer == customer_id
        && ID != invoice_id
    ]
    {
        previous_balance_of_unpaid_invoices = previous_balance_of_unpaid_invoices + curr_invoice.Amount_Due;
    }
}
get_invoice.Previous_Balance = previous_balance_of_unpaid_invoices;
get_invoice.Total_Amount_Due = current_amount_due + previous_balance_of_unpaid_invoices;
```

```deluge
// invoice.recalculate_balances_from(invoice_id) — cascade
thisapp.invoice.invoice_balance_updates(invoice_id);
get_invoice = Invoice[ID == invoice_id];
if(get_invoice != null && get_invoice.Invoice_Date != null && get_invoice.Customer != null)
{
    customer_id = get_invoice.Customer.ID;
    for each inv in Invoice[Invoice_Date > get_invoice.Invoice_Date && Customer == customer_id]
    {
        thisapp.invoice.invoice_balance_updates(inv.ID);
    }
}
```

---

## 2. Target architecture

### 2.1 Core functions

| Function | File | Role |
|----------|------|------|
| `invoice.invoice_balance_updates(invoice_id)` | `Custom Functions/invoice/invoice_balance_updates` | **Main engine** — canonical rules above |
| `invoice.recalculate_balances_from(invoice_id)` | `Custom Functions/invoice/recalculate_balances_from` | **NEW wrapper** — update invoice + cascade to later invoices |
| `invoice.handle_previous_invoice_balances(...)` | `Custom Functions/invoice/handle_previous_invoice_balances` | **Deprecate** — delegate to new engine |

### 2.2 Standard replacement pattern

**Replace all inline loops with:**

```deluge
thisapp.invoice.recalculate_balances_from(invoice_id);
```

**On form `input` (user input / on load preview — current invoice only):**

```deluge
thisapp.invoice.invoice_balance_updates(input.ID);
// copy Previous_Balance / Total_Amount_Due back to input if needed
```

---

## 3. Legacy logic in `.ds` (to be replaced)

| Legacy set | What it does today | Action |
|------------|-------------------|--------|
| **Month-based (OLD)** | `toStartOfMonth()` + `Customer_Code` + often `Total_Amount_Due = Grand_Total` | **Replace** with canonical rules |
| **Added_Time (live payment add)** | `Added_Time < zoho.currenttime`, cascade commented out | **Replace** with date-based + cascade |
| **Date-based, no Blueprint (partial)** | Current `invoice_balance_updates` + some form workflows | **Update** — add Blueprint filter per rule #3 |

---

## 4. Phase 0 — Sync repo from `.ds` first (mandatory)

Before standardizing, align `application/` with live export. **If repo ≠ `.ds`, use `.ds`.**

| Application file | Live workflow in `.ds` | Sync status | Action |
|------------------|--------------------------|-------------|--------|
| `forms/Payment Received/workflow/Handle_Successful_Submiss.deluge` | `Handle_Successful_Submiss` ~L26147 | ✅ Synced to live (Added_Time) | Will change in Step 16 to date-based |
| `forms/Payment Received/workflow/Handle_Deletion.deluge` | `Handle_Successful_Deletio` ~L26374 | ❌ **Mismatch** | Rewrite from `.ds` L26387–L26455 |
| `forms/Invoice/workflow/Load_of_the_form_Initiali.deluge` | `Load_of_the_form_Initiali` ~L36951 | ✅ Matches | Update in Step 14 (add Blueprint filter) |
| `forms/Invoice/workflow/actions/Send_Invoice.deluge` | `Send_Invoice` ~L42648 | ✅ Synced | Standardize in Step 19 |
| `blueprints/pro forma invoice 1/.../script_02.deluge` | **Not in `.ds`** | ❌ Stale | Not in migration |
| `forms/Invoice/workflow/actions/Mark_As_Sent.deluge` | **Not in `.ds`** | ❌ Stale | Not in migration |
| `forms/Invoice/workflow/actions/Duplicate_Invoice.deluge` | **Not in `.ds`** | ❌ Stale | Not in migration |

---

## 5. Complete file change list (30 files)

### Tier 1 — Core (3 files)

| # | File | Change type |
|---|------|-------------|
| 1 | `application/Custom Functions/invoice/invoice_balance_updates` | Update to canonical rules (add Blueprint filter) |
| 2 | `application/Custom Functions/invoice/handle_previous_invoice_balances` | Deprecate / delegate |
| 3 | `application/Custom Functions/invoice/recalculate_balances_from` | **Create new** |

### Tier 2 — Scheduled invoice creation (6 files)

| # | File | `.ds` function |
|---|------|----------------|
| 4 | `application/Custom Functions/invoice/create_invoice` | ~L15787 |
| 5 | `application/Custom Functions/invoice/create_invoice_current_monthly` | ~L16883 |
| 6 | `application/Custom Functions/invoice/create_invoice_current_not_monthly` | ~L17715 |
| 7 | `application/Custom Functions/invoice/create_invoice_previous_monthly` | ~L18544 |
| 8 | `application/Custom Functions/invoice/create_invoice_previous_not_monthly` | ~L19489 |
| 9 | `application/Custom Functions/invoice/create_new_invoice_no_for_duplicate` | ~L20432 |

### Tier 3 — Invoice form workflows (6 files)

| # | File | `.ds` workflow | Lines |
|---|------|----------------|-------|
| 10 | `application/forms/Invoice/workflow/Successful_form_submissio.deluge` | `Successful_form_submissio` | ~L25032 |
| 11 | `application/forms/Invoice/workflow/Handle_Invoice_Date.deluge` | `Handle_Invoice_Date` | ~L25344 |
| 12 | `application/forms/Invoice/workflow/Handle_Customer_Code_Chan.deluge` | `Handle_Customer_Code_Chan` | ~L24982 |
| 13 | `application/forms/Invoice/workflow/Customer_Name_Trigger_Wor.deluge` | `Customer_Name_Trigger_Wor` | ~L37685 |
| 14 | `application/forms/Invoice/workflow/Load_of_the_form_Initiali.deluge` | `Load_of_the_form_Initiali` | ~L36951 |
| 15 | `application/forms/Invoice/workflow/Handle_Deletion_Of_Invoic.deluge` | `Handle_Deletion_Of_Invoic` | ~L24617 |

### Tier 4 — Payment Received (2 files)

| # | File | `.ds` workflow | Lines |
|---|------|----------------|-------|
| 16 | `application/forms/Payment Received/workflow/Handle_Successful_Submiss.deluge` | `Handle_Successful_Submiss` | ~L26049 |
| 17 | `application/forms/Payment Received/workflow/Handle_Deletion.deluge` | `Handle_Successful_Deletio` | ~L26374 |

### Tier 5 — Other form workflow (1 file)

| # | File | `.ds` workflow | Lines |
|---|------|----------------|-------|
| 18 | `application/forms/Notify Credits Available/workflow/Send_Invoice_To_Customer.deluge` | `Send_Invoice_To_Customer` | ~L26576 |

### Tier 6 — Invoice record action (1 file)

| # | File | `.ds` function | Lines |
|---|------|----------------|-------|
| 19 | `application/forms/Invoice/workflow/actions/Send_Invoice.deluge` | `Send_Invoice` | ~L42648 |

### Tier 7 — Invoice Blueprint (5 files)

| # | File | Transition | `.ds` lines |
|---|------|------------|-------------|
| 20 | `application/blueprints/Invoice_Blueprint/transitions/Approve/after/unconditional/script_01.deluge` | Approve | ~L40692 |
| 21 | `application/blueprints/Invoice_Blueprint/transitions/Reject/after/unconditional/script_01.deluge` | Reject | ~L40816 |
| 22 | `application/blueprints/Invoice_Blueprint/transitions/Resubmit/after/unconditional/script_01.deluge` | Resubmit | ~L40915 |
| 23 | `application/blueprints/Invoice_Blueprint/transitions/Send_For_Approval/after/unconditional/script_01.deluge` | Send For Approval | ~L40951 |
| 24 | `application/blueprints/Invoice_Blueprint/blueprint.json` | Embedded scripts | ~32 inline matches |

### Tier 8 — Debit Note Blueprint (5 files)

| # | File | Transition |
|---|------|------------|
| 25 | `application/blueprints/Debit_Note_Blueprint/transitions/Approve/after/unconditional/script_01.deluge` | Approve |
| 26 | `application/blueprints/Debit_Note_Blueprint/transitions/Reject/after/unconditional/script_01.deluge` | Reject |
| 27 | `application/blueprints/Debit_Note_Blueprint/transitions/Resubmit/after/unconditional/script_01.deluge` | Resubmit |
| 28 | `application/blueprints/Debit_Note_Blueprint/transitions/Send_For_Approval/after/unconditional/script_01.deluge` | Send For Approval |
| 29 | `application/blueprints/Debit_Note_Blueprint/blueprint.json` | Embedded scripts |

### Tier 9 — Re-export after deploy (1 file)

| # | File |
|---|------|
| 30 | `XMT___Billing_System(1).ds` |

### Files explicitly NOT changed

| File | Reason |
|------|--------|
| `application/forms/Invoice/workflow/User_Input_Trigger_Workfl.deluge` | Already uses `Total_Amount_Due = Amount_Due + Previous_Balance` |
| `application/forms/Invoice/workflow/Disable_Fields3.deluge` | Disables field on load only |

---

## 6. File-by-file implementation plan

Execute in this order. For each file: **(1) sync from `.ds` if mismatched → (2) replace inline logic with function call.**

---

### Step 1 — `invoice_balance_updates` (Tier 1 #1)

**Path:** `application/Custom Functions/invoice/invoice_balance_updates`  
**`.ds` ref:** L20795–L20814

**Change from live today:**
- Add `Blueprint.Current_Stage in {"Sent","Overdue","Partially Paid"}`
- Add `ID != invoice_id` (exclude self)
- Keep `Invoice_Date < invoice_date`, `Customer == customer_id`, `Amount_Due > 0`

**Plan:**
- [ ] Implement canonical rules from Section 1.1
- [ ] This is the **only** place that defines the calculation

---

### Step 2 — `recalculate_balances_from` (Tier 1 #3, NEW)

**Path:** `application/Custom Functions/invoice/recalculate_balances_from`

**Plan:**
- [ ] Create function per Section 1.1
- [ ] Cascade: `Invoice_Date > get_invoice.Invoice_Date && Customer == customer_id`

---

### Step 3 — `handle_previous_invoice_balances` (Tier 1 #2)

**Path:** `application/Custom Functions/invoice/handle_previous_invoice_balances`  
**`.ds` ref:** L20773–L20793

**Plan:**
- [ ] Rewrite to use canonical rules (date-based, not `toStartOfMonth`)
- [ ] Keep map return shape (`Previous_Balance`, `Total_Amount_Due`, `Overdue_Charges`) for create-invoice callers until they migrate to Step 2 pattern

---

### Steps 4–9 — Create invoice functions (Tier 2)

| Step | File | Plan |
|------|------|------|
| 4 | `create_invoice` | Replace `handle_previous_invoice_balances` with canonical engine after insert |
| 5 | `create_invoice_current_monthly` | Same |
| 6 | `create_invoice_current_not_monthly` | Same |
| 7 | `create_invoice_previous_monthly` | Same |
| 8 | `create_invoice_previous_not_monthly` | Same |
| 9 | `create_new_invoice_no_for_duplicate` | Same |

---

### Step 10 — `Successful_form_submissio.deluge` (Tier 3 #10)

**`.ds` ref:** L25045–L25062

**Plan:**
- [ ] Replace inline loop + cascade with `thisapp.invoice.recalculate_balances_from(input.ID)`

---

### Step 11 — `Handle_Invoice_Date.deluge` (Tier 3 #11)

**`.ds` ref:** L25371–L25384

**Plan:**
- [ ] Replace inline loop with `invoice_balance_updates(input.ID)` (no cascade on user input)

---

### Step 12 — `Handle_Customer_Code_Chan.deluge` (Tier 3 #12)

**`.ds` ref:** L25005–L25018

**Plan:** Same as Step 11.

---

### Step 13 — `Customer_Name_Trigger_Wor.deluge` (Tier 3 #13)

**`.ds` ref:** L37793–L37803

**Plan:** Same as Step 11.

---

### Step 14 — `Load_of_the_form_Initiali.deluge` (Tier 3 #14)

**`.ds` ref:** L36970–L36977

**Plan:**
- [ ] Replace inline loop with canonical logic (Blueprint filter + date-based)
- [ ] On load preview: call engine if `input.ID` exists, else inline same filter on `input`

---

### Step 15 — `Handle_Deletion_Of_Invoic.deluge` (Tier 3 #15)

**`.ds` ref:** L24633–L24635

**Plan:**
- [ ] Replace `eomonth(0)` cascade loop with `recalculate_balances_from` on each later invoice for customer (or one helper call per affected invoice)

---

### Step 16 — `Handle_Successful_Submiss.deluge` (Tier 4 #16)

**`.ds` ref:** L26147–L26163

**Confirmed:** Date-based (rule #8) — **remove** `Added_Time < zoho.currenttime`.

**Plan:**
- [ ] After amount paid/due update, call `thisapp.invoice.recalculate_balances_from(curr_get_invoice.ID)`
- [ ] Remove inline loop and commented-out cascade block

---

### Step 17 — `Handle_Deletion.deluge` → sync to `Handle_Successful_Deletio` (Tier 4 #17)

**`.ds` ref:** L26413–L26423

**Phase 0 first:**
- [ ] Rewrite from `.ds` L26374–L26455
- [ ] Consider rename to `Handle_Successful_Deletio.deluge`

**Then standardize:**
- [ ] Replace OLD month-based balance block with `recalculate_balances_from(curr_get_invoice.ID)`

---

### Step 18 — `Send_Invoice_To_Customer.deluge` (Tier 5 #18)

**`.ds` ref:** L26744–L26753

**Plan:**
- [ ] Remove misc-charge exemption (rule #6) — same rules for all invoices
- [ ] Replace inline loop with `recalculate_balances_from(getInvoice.ID)`

---

### Step 19 — `Send_Invoice.deluge` action (Tier 6 #19)

**`.ds` ref:** L42742–L42751 and L42861–L42870

**Plan:**
- [ ] Replace both `previoustotalAmountDue` blocks with `recalculate_balances_from(input.ID)`
- [ ] Stop setting `Total_Amount_Due = Grand_Total` — use canonical formula
- [ ] Keep email/journal/blueprint blocks unchanged

---

### Steps 20–23 — Invoice Blueprint scripts (Tier 7)

**Each plan:**
- [ ] Remove `previoustotalAmountDue` + `toStartOfMonth()` loops
- [ ] Call `thisapp.invoice.recalculate_balances_from(input.ID)`
- [ ] Stop forcing `Total_Amount_Due = Grand_Total`

---

### Step 24 — `Invoice_Blueprint/blueprint.json` (Tier 7 #24)

**Plan:** Mirror Steps 20–23 in embedded JSON strings.

---

### Steps 25–28 — Debit Note Blueprint scripts (Tier 8)

**Plan per file:**
- [ ] Replace `eomonth(0)` cascade loops with `recalculate_balances_from` pattern
- [ ] Keep debit note `Amount_Due = Grand_Total` setup; only change invoice cascade mechanism

---

### Step 29 — `Debit_Note_Blueprint/blueprint.json` (Tier 8 #29)

**Plan:** Mirror Steps 25–28 in JSON.

---

### Step 30 — Re-export `.ds`

**Plan:**
- [ ] Deploy to Zoho Creator
- [ ] Re-export to `XMT___Billing_System(1).ds`

---

## 7. Execution summary (checklist)

```
Phase 0 — Sync
[ ] Handle_Deletion.deluge ← .ds Handle_Successful_Deletio
[ ] Confirm stale files (Mark_As_Sent, Duplicate_Invoice, pro forma script_02)

Phase 1 — Core
[ ] Step 1  invoice_balance_updates (add Blueprint filter)
[ ] Step 2  recalculate_balances_from (new)
[ ] Step 3  handle_previous_invoice_balances (delegate)

Phase 2 — Callers
[ ] Steps 4–9   create_invoice*
[ ] Steps 10–15 invoice workflows
[ ] Steps 16–17 payment workflows (date-based, not Added_Time)
[ ] Step 18     Send_Invoice_To_Customer
[ ] Step 19     Send_Invoice action
[ ] Steps 20–24 Invoice blueprint
[ ] Steps 25–29 Debit blueprint
[ ] Step 30     re-export .ds
```

---

## 8. Post-migration audit

Run from repo root — expect **zero** matches outside core functions (and comments):

```bash
rg "previoustotalAmountDue|previous_balance_of_unpaid|handle_previous_invoice_balances|toStartOfMonth\(\)|Added_Time < zoho" application/
```

---

## 9. Test matrix (minimum)

| Scenario | Trigger file | Verify |
|----------|--------------|--------|
| New invoice, customer has older **Sent** unpaid invoice | `Successful_form_submissio` | Counts older invoice in `Previous_Balance` |
| New invoice, customer has older **Draft** invoice only | `Successful_form_submissio` | Draft **not** counted (Blueprint filter) |
| Change invoice date | `Handle_Invoice_Date` | Recalculates correctly |
| Approve invoice | Blueprint Approve | Current + later invoices updated; `Total_Amount_Due = Amount_Due + Previous_Balance` |
| Send invoice (approved, no credit) | `Send_Invoice` action | Balance + stage change |
| Record payment | `Handle_Successful_Submiss` | Date-based; paid invoice + later invoices cascaded |
| Delete payment | `Handle_Successful_Deletio` | Reverses balances |
| Delete invoice | `Handle_Deletion_Of_Invoic` | Later invoices recascaded |
| Scheduled invoice create | `create_invoice*` | Initial balance uses canonical rules |
| Misc charge invoice | Any trigger | Same rules as normal invoice (rule #6) |

---

## 10. Open decisions log

| Date | Decision | Status |
|------|----------|--------|
| 2026-05-29 | Rules #1–#8 confirmed (see Section 1) | ✅ Done |
| | Debit notes affect invoice `Previous_Balance` (rule #9) | ⏳ TBD later |
| | Rename `Handle_Deletion` → `Handle_Successful_Deletio` | Dev task |
| | Remove stale action files | Dev task |

---

*Last updated: 2026-05-29 — rules confirmed; source audit from `XMT___Billing_System(1).ds` (51429 lines).*
