# Phase 2 — On-Load Prefill for Convert (Add Form)

Part of: [After 13 — Convert defer save](00-overview.md)

## Objective

When the Credit Note **add** form opens from convert (URL prefills `Reference_Invoice`), populate header fields, line subforms, and `Credit_Mode` from the source invoice — without creating a database record.

## Primary files

- **New (recommended):** `application/forms/Credit Note/workflow/Handle_Convert_Prefill.deluge`
- **Or extend:** `application/forms/Credit Note/workflow/Load_Of_The_Form_during_C1.deluge`

## Dependency

- Phase 1 deployed (convert opens add form with `Reference_Invoice` + `Customer` URL params).

---

## Workflow definition

| Property | Value |
|----------|-------|
| Trigger | `on load` |
| Record event | `on add` |
| Condition | `input.Reference_Invoice != null` |

**Distinguish convert vs manual add with URL param:**

- Manual Add: user picks `Reference_Invoice` later → `on user input` in `Handle_reference_invoice_2` handles clone.
- Convert Add: `Reference_Invoice` already set from URL on load → this workflow runs once.

Optional guard: only prefill when `input.ID == null` and lines are empty (avoid double-clone on refresh).

---

## Actions (in order)

### 1. Load source invoice

```deluge
ref_invoice = Invoice[ID == input.Reference_Invoice];
```

### 2. Header fields

Copy from source invoice (mirror current `Convert_To_Credit_Note` insert map):

- Customer block (name, TIN, ID type, registration, SST, code, email, phone, address)
- Delivery address
- `Subscriptions`, `Invoice_For_Usage`, `Payment_Term`, `Enable_Reminder`
- `Charge_Category`, `Announcement`, `Attachment`
- `Base_Currency`, `Invoice_Currency`, `Exchange_Rate`
- Sub/tax/grand totals per charge category and header totals
- `Payable_To`
- `Invoice_Date` = `zoho.currentdate`
- `Due_Date` = `zoho.currentdate.addDay(Payment_Term.Days)`
- `Credits_Used` = 0, `Refund` = 0, `Credits_Remaining` = grand total after lines load

Do **not** set `Invoice_No` — assigned on Submit (`Handle_Invoice_Creation1`).

### 3. Line subforms

Clone from reference invoice into CN subforms:

- `Monthly_Rental`
- `Internet_Charges`
- `Call_Charges`

Use the same field mapping as `Handle_reference_invoice_2.deluge` (lines 74–136). Phase 3 extracts this to a shared function.

```deluge
clear Monthly_Rental;
clear Internet_Charges;
clear Call_Charges;
// ... insert rows from ref_invoice ...
```

### 4. Credit_Mode (Step 11 rules)

```deluge
ref_stage = ref_invoice.Blueprint.Current_Stage;
if(ref_stage == "Sent" || ref_stage == "Overdue")
{
    input.Credit_Mode = "Mode A - Debt Reduction";
}
else if(ref_stage == "Partially Paid" || ref_stage == "Paid")
{
    input.Credit_Mode = "Mode B - Open Credit";
}
```

If stage ineligible, alert and `clear Reference_Invoice` (should not happen if Phase 1 stage check is correct).

### 5. Recalculate totals

```deluge
input.User_Input_Trigger = !input.User_Input_Trigger;
```

Ensures tax/grand total workflows run after lines are inserted.

---

## Interaction with existing on-load workflows

| Workflow | Concern |
|----------|---------|
| `Load_Of_The_Form_during_C1` | Sets org **Supplier** on add — runs on same `on add` / `on load`; verify supplier not overwritten by invoice copy |
| `Load_of_the_form_Initiali1` | Sets `Is_Initialization`, toggles triggers — test order so status does not jump to Open |
| `User_Input_Trigger_Workfl2` | Must not promote to Open before Submit (Step 04 hardening) |

**Action:** Test workflow execution order in Creator sandbox after implementation.

---

## LHDN on prefill

| Approach | Recommendation |
|----------|----------------|
| Full LHDN document API (like `Handle_reference_invoice_2`) | **No** — slow on every convert open |
| Light check: UUID + Public Link present | **Optional** in Phase 1 convert action |
| Full UUID validation | On **Submit** via `Handle_Validation_Submiss2` |

---

## Zoho safety

- **Sandbox test:** Confirm URL param `Reference_Invoice={id}` prefills lookup on add form.
- **Fallback:** Hidden field `Convert_Source_Invoice_ID` in URL if lookup prefill fails.
- **Subform insert on add:** Same pattern as `Handle_reference_invoice_2` (`input.Monthly_Rental.insert(...)`).

---

## Exit criteria (Phase 2)

- [ ] Convert opens add form with full header + lines prefilled
- [ ] `Credit_Mode` set correctly from invoice stage
- [ ] Form shows **Submit**, not **Update**
- [ ] CN **not** in Credit Notes list until Submit
- [ ] Manual Add path unchanged (user picks reference → `Handle_reference_invoice_2`)
- [ ] New/updated workflow synced to `XMT___Billing_System.ds`
