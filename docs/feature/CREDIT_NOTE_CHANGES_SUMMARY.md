# Credit Note System — What We Actually Built

A single reference for the full scope of changes made to the Credit Note module, from first fix to final unified state. Strips out all the back-and-forth iterations.

---

## The Problem We Started With

The Credit Note module had no structure. Key issues:

- No mandatory link between a Credit Note and the Invoice it corrects
- The "Convert to Credit Note" button inserted a Draft CN record on click — before the user confirmed anything
- Blueprint stages were inconsistent; CNs could jump to Open/Closed without going through approval
- Apply Credits and Create Refund Note actions had no proper guards
- LHDN submission did not include a reference invoice payload
- Two artificial code paths ("Mode A" and "Mode B") were introduced during fixing, then later discovered to be unnecessary and actively harmful

---

## What We Changed — In Correct Final Order

### 1. Reference Invoice — Mandatory Link

**File:** `application/forms/Credit Note/workflow/Handle_reference_invoice_2.deluge`  
**File:** `application/forms/Credit Note/workflow/Handle_Validation_Submiss2.deluge`  
**File:** `application/forms/Credit Note/Credit_Note.deluge`

- Added `Reference_Invoice` as a required field on the Credit Note form
- When `Reference_Invoice` is selected, the system checks the invoice's LHDN UUID — if missing, the field is rejected immediately (cannot create a CN against an uninvoiced record)
- Save is blocked if `Reference_Invoice` is null or empty
- Only invoices with status **Sent, Overdue, Partially Paid, or Paid** are eligible as reference invoices — any other stage is rejected with an alert

---

### 2. Line Items — Clone from Reference Invoice, Reduce Only

**File:** `application/forms/Credit Note/workflow/Handle_reference_invoice_2.deluge`  
**File:** `application/forms/Credit Note/workflow/Handle_Convert_Prefill.deluge`  
**File:** `application/Custom Functions/credit_note/prefill_from_reference_invoice`  
**File:** `application/forms/Credit Note/workflow/Handle_Validation_Submiss2.deluge`  
**File:** `application/forms/Credit Note/workflow/Disable_Fields20.deluge`

- When `Reference_Invoice` is selected (manual path) or set via URL param (convert path), line items are cloned from the source invoice automatically
- Item identity fields (item code, tax rate, unit price) are **locked read-only** — user cannot change what the line is for
- User may only **reduce** quantity or amount per line — cannot increase beyond source values
- Adding new line rows is blocked
- Save validation checks each line: CN line amount ≤ source invoice line amount

Centralised in custom function `credit_note.prefill_from_reference_invoice` — both manual selection and convert path call the same function. This is the single source of truth for field mapping.

---

### 3. Convert Path — No Insert on Click

**File:** `application/forms/Invoice/workflow/actions/Convert_To_Credit_Note.deluge`  
**File:** `application/forms/Credit Note/workflow/Handle_Convert_Prefill.deluge`

**Old (wrong):** Convert button inserted a Draft CN record immediately on click.  
**Correct:** Convert button opens the Credit Note add form prefilled with URL parameters (`Reference_Invoice`, `Customer`, `Customer_Code`). No record is created until the user clicks Submit.

- The on-load workflow `Handle_Convert_Prefill` detects the URL params and prefills the full header and line items
- Form shows **Submit** (add mode) — not Update
- If the user closes the popup without submitting, no CN record is left behind
- The convert action only blocks if `remaining_creditable <= 0` (no credit room left). Over-amount scenarios are caught at Submit, not at Convert

---

### 4. Blueprint Structure — Correct Stage Transitions

**File:** `application/blueprints/Credit_Note_Blueprint/...`

Correct stage flow:

```
Draft → Pending Approval → Approved → Open
                                    → Closed
       → Rejected → (fix) → Pending Approval
```

- Added `Approved_to_Closed` transition
- Added `Converted_to_Open` transition (Approved → Open when credits remain)
- Disabled `Revert_to_Pending_Approval` auto-revert — CNs do not bounce back on their own
- No workflow directly writes `Open` or `Closed` on Draft/Pending/Rejected records — stage changes only happen via `changeStage(...)` at the correct point

---

### 5. Cumulative Cap — Cannot Over-Credit an Invoice

**File:** `application/forms/Credit Note/workflow/Handle_Validation_Submiss2.deluge`  
**File:** `application/blueprints/Credit_Note_Blueprint/transitions/Approve/after/unconditional/script_01.deluge`

The total of all Credit Notes raised against one invoice must never exceed the original invoice amount.

**At save (validate trigger):**
- Sums Grand_Total of all CNs against the same Reference_Invoice with stage in `{Approved, Closed, Open, Pending Approval}`
- Subtracts from original invoice total to get `remaining_creditable`
- Blocks save if this CN's calculated total exceeds `remaining_creditable`
- Uses line totals calculated at validate time — not the potentially stale `input.Grand_Total`

**At approval (approve script, before applying):**
- Rechecks the cap using current DB values (a concurrent approval or late payment may have changed the picture)
- If cap exceeded at approval, transitions CN back to **Pending Approval** via `changeStage` and logs the breach — does not silently approve

---

### 6. Approval — Unified Auto-Apply Rule

**File:** `application/blueprints/Credit_Note_Blueprint/transitions/Approve/after/unconditional/script_01.deluge`

This is the core billing logic change. The old system had "Mode A" and "Mode B" that branched approval behaviour based on a field set at creation. Mode A silently discarded remaining credits. Mode B never auto-applied anything.

**Replaced with one rule that handles every invoice state:**

```
apply_amount      = min(CN Grand_Total, ref_invoice.Amount_Due)
credits_remaining = CN Grand_Total − apply_amount

if credits_remaining = 0  →  CN → Closed
if credits_remaining > 0  →  CN → Open
```

What this produces for each invoice state:

| Invoice state at approval | Amount_Due | CN amount | Applied | Credits_Remaining | CN result |
|---|---|---|---|---|---|
| Sent, no drift | 1000 | 1000 | 1000 | 0 | Closed |
| Sent, drift (payment before approval) | 300 | 1000 | 300 | 700 | Open |
| Partially Paid | 400 | 500 | 400 | 100 | Open |
| Paid | 0 | 500 | 0 | 500 | Open |

When `apply_amount > 0`:
- An `Apply_Credit_To_Invoice_Line` record is inserted
- Invoice `Credits_Applied_Total` and `Amount_Due` are recalculated
- Invoice stage is updated (Paid / Partially Paid / Sent / Overdue) based on new Amount_Due
- `calculate_invoice_previous_balance_and_total_amount_due` and `calculate_opening_balance_by_tenancy` are called to propagate the balance change
- An audit row is inserted into `Invoice_Related_List`

CN fields updated:
- `Credit_Applied_Invoices` subform — refreshed from all `Apply_Credit_To_Invoice_Line` rows for this CN
- `Credits_Used` — sum of all applied amounts
- `Credits_Remaining` — CN Grand_Total minus Credits_Used

---

### 7. Action Visibility — What Shows When

**File:** `application/forms/Credit Note/Credit_Notes.deluge`

| Action | Visible when |
|---|---|
| Apply Credits to Invoices | CN stage = **Open** |
| Create Refund Note | CN stage = **Open** |
| Submit Credit Note to LHDN | CN stage = **Closed** |

`Approved` is no longer a valid resting stage — the approve script always transitions the CN to Open or Closed immediately. Actions tied to `Approved` have been removed.

---

### 8. LHDN Submission — Reference Payload

**File:** `application/forms/Credit Note/workflow/actions/Submit_Credit_Note_to_LHD1.deluge`

- Only visible and executable when CN stage = **Closed**
- Payload includes `Reference_Invoice` UUID and invoice number in the `reference_invoice_list`
- Deduplication of references is validated before submission

---

### 9. Retiring Credit_Mode Field (Step B — pending)

**Not yet deployed.** Deploy only after unified rule (Step A) is confirmed working in production.

Files to update:
- Delete `application/Custom Functions/credit_note/credit_mode_from_invoice_stage`
- Remove `input.Credit_Mode = prefill_data.get("credit_mode")` from `Handle_reference_invoice_2.deluge` and `Handle_Convert_Prefill.deluge`
- Remove `disable Credit_Mode` from `Disable_Fields20.deluge`
- Remove `Credit_Mode as "Credit Mode"` from `Credit_Note_Report.deluge`
- Remove `Credit_Mode` from `Credit_Note.deluge`
- Delete the field from the Credit Note form in Creator UI (**last action** — permanent data loss)
- Re-export `XMT___Billing_System.ds`

Before deleting: confirm `grep -r "Credit_Mode" application/` returns zero results.

---

### 10. User-Facing Messages — Cleaned Up

**Priority 1 — already done or in current diff:**

| File | Change |
|---|---|
| `script_01.deluge` lines 335 & 340 | Replace `"Unified auto-apply complete. CN " + input.ID + ...` with human-readable finance language using `input.Invoice_No` and RM amounts |
| `script_01.deluge` line 16 | Replace raw variable dump cap-exceeded message with clear finance language |
| `Handle_Call_Charges_Item3.deluge` line 16 | Replace `info "Ensure Exchange Rate is not empty"` with `alert "Please enter the Exchange Rate before adding line items."` |
| `Handle_Internet_Charges_I2.deluge` line 16 | Same as above |
| `Handle_Monthly_Rental_Ite2.deluge` line 16 | Same as above |

**Priority 2 — clean up when convenient:**

| File | Change |
|---|---|
| `Handle_Validation_Submiss2.deluge` line 28 | Remove `Reference_Invoice` field name from alert text |
| `Handle_reference_invoice_2.deluge` line 142 | Replace "Invoice stage" with "invoice with status"; list eligible statuses |
| `Handle_Convert_Prefill.deluge` line 128 | Same as above |
| `Submit_Credit_Note_to_LHD1.deluge` line 3 | Change `info` → `alert`; rewrite message to explain what action is needed |

---

## Files Changed — Full List

| File | What changed |
|---|---|
| `application/blueprints/Credit_Note_Blueprint/transitions/Approve/after/unconditional/script_01.deluge` | Unified auto-apply rule; cumulative cap recheck at approval; user-facing messages |
| `application/forms/Credit Note/workflow/Handle_Validation_Submiss2.deluge` | Mandatory reference invoice; reduce-only line guard; cumulative cap at save; removed Credit_Mode block |
| `application/forms/Credit Note/workflow/Handle_reference_invoice_2.deluge` | Eligibility check (stage-based, not mode-based); line clone; Credit_Mode lines removed (Step B) |
| `application/forms/Credit Note/workflow/Handle_Convert_Prefill.deluge` | New on-load prefill for convert path; Credit_Mode line removed (Step B) |
| `application/forms/Credit Note/workflow/Handle_Call_Charges_Item3.deluge` | Alert message fix |
| `application/forms/Credit Note/workflow/Handle_Internet_Charges_I2.deluge` | Alert message fix |
| `application/forms/Credit Note/workflow/Handle_Monthly_Rental_Ite2.deluge` | Alert message fix |
| `application/forms/Credit Note/workflow/Disable_Fields20.deluge` | Lock item identity fields; Credit_Mode disable removed (Step B) |
| `application/forms/Credit Note/workflow/actions/Submit_Credit_Note_to_LHD1.deluge` | Alert instead of info; correct LHDN reference payload |
| `application/forms/Invoice/workflow/actions/Convert_To_Credit_Note.deluge` | No insert on click; opens add form with URL params |
| `application/forms/Credit Note/Credit_Notes.deluge` | Action conditions: Apply/Refund → Open only; LHDN → Closed only |
| `application/Custom Functions/credit_note/prefill_from_reference_invoice` | Shared line-clone logic for both paths; eligibility by stage (no Credit_Mode) |
| `application/Custom Functions/credit_note/credit_mode_from_invoice_stage` | **Delete (Step B)** |
| `application/forms/Credit Note/Credit_Note_Report.deluge` | Remove Credit_Mode column (Step B) |
| `application/forms/Credit Note/Credit_Note.deluge` | Remove Credit_Mode field declaration (Step B) |
| Creator UI — Credit Note form | Delete Credit_Mode field (Step B — last action) |
| `XMT___Billing_System.ds` | Mirror all above after each deploy step |

---

## What We Did NOT Touch

**Refund Notes** — the Refund Note form and all its workflows were not modified at any point during this workstream.

The only refund-adjacent change was the **visibility condition** of the "Create Refund Note" button on the Credit Note list view (`Credit_Notes.deluge`). The condition changed from `(Approved || Open) && Mode B` to `Open`. This controls when the button appears — not the creation logic, not the Refund Note form itself.

Files that remain exactly as they were before our work:
- `application/forms/Credit Note/workflow/actions/Create_Refund_Note_From_C.deluge`
- `application/forms/Refund Note/` — entire form, all workflows, LHDN action
- `application/Custom Functions/refund_note/generate_refund_note_no`

---

## Deploy Order

1. **Step A** — All changes except Step B items. Verify T-A1 to T-A8 in sandbox.
2. **Confirm** — No CN stuck at Approved; Credits_Remaining correct; Apply/Refund visible only on Open.
3. **Step B** — Retire Credit_Mode. Confirm `grep -r "Credit_Mode" application/` = zero. Delete field in Creator UI last.

Do not merge Step A and Step B into one deploy.
