# Credit Note — Current System vs Correct Flow

Compared against `creditNote_Flow.md`.

---

## Convert from Invoice path

**1.** After user clicks **Convert to Credit Note**, the credit note does not reliably stay in **Draft** — when the popup opens, `Load_of_the_form_Initiali1` fires `User_Input_Trigger`, and `User_Input_Trigger_Workfl2` sets `Status = "Open"` because `Credits_Remaining > 0`.  
= **[Correction]** It should stay **Draft** until the user saves, sends for approval, and gets **Approved**. **Open** should only happen **after approval**, when credit is applied or refunded.

**2.** Convert does **not** set `Reference_Invoice` to the source invoice (field does not exist on Credit Note form; Debit Note convert does set it).  
= **[Correction]** On convert, set `Reference_Invoice = source invoice ID` so the credit is auditable and available for LHDN reference.

**3.** Convert does **not** call `changeStage(..., "Draft", ...)` after insert.  
= **[Correction]** Explicitly set blueprint to **Draft** after insert.

**4.** CN number is generated **twice** on convert: once in `Convert_To_Credit_Note` insert (`Invoice_No=generate_credit_note_no()`), then again in `Handle_Invoice_Creation1` on add success.  
= **[Correction]** Generate CN number **once** — only in `Handle_Invoice_Creation1` on add; convert insert should **not** set `Invoice_No`.

**5.** Convert does **not** update or link the source invoice in any way (no flag, no subform, no balance change).  
= **[Correction]** At minimum link via `Reference_Invoice`; optionally surface on the invoice that a credit note exists. Balance change should happen only when credit is **applied**, not at convert — but the **link** should exist immediately.

**6.** Convert sets `Invoice_Date = today` and recalculates `Due_Date` from today, not from the source invoice date.  
= **[Correction]** For invoice-originated credits, `Invoice_Date` should be the **credit note issue date** (today can be OK), but the link to the **original invoice date/number** should be on `Reference_Invoice`, not lost.

**7.** Convert always copies the **full** invoice amount as `Credits_Remaining = Grand_Total` with no prompt for partial credit.  
= **[Correction]** User should review in **Draft**, adjust lines for partial credit, then save — but status must not jump to **Open** before approval (see #1).

**8.** Convert button condition uses `"paid"` (lowercase) but not `"Paid"` — may hide or show the button inconsistently.  
= **[Correction]** Match blueprint stage names exactly: `Sent`, `Partially Paid`, `Paid`, `Overdue`.

**9.** After convert, user can use **Apply Credits to Invoices** if status is **Open**, even if never went through **Pending Approval → Approved**.  
= **[Correction]** Apply credit should only be allowed at **Approved** (or **Open** only if it was **Approved** first). Not straight from Draft-via-convert.

**10.** Apply-credit flow does **not** prefer or default to the **source invoice** from convert.  
= **[Correction]** When `Reference_Invoice` is set, apply-credit popup should default/preselect that invoice (especially if unpaid).

---

## Manual create path

**11.** On manual Add, after first save, reopening the form triggers the same `User_Input_Trigger` logic and can set **Open** before approval.  
= **[Correction]** New credit note should stay **Draft** until approval workflow completes.

**12.** On manual save, `Handle_Invoice_Creation1` correctly generates CN number and sets **Draft** — entry prefill and first-save numbering match the correct flow.  
(No correction needed.)

---

## Shared — approval & status (both paths)

**14.** `User_Input_Trigger_Workfl2` sets `Status = "Open"` or `"Closed"` on **every form load/edit** when `input.ID != null`, with **no check** for current blueprint stage (Draft / Pending Approval / Approved).  
= **[Correction]** Open/Closed should only be set **after Approved**, when `Credits_Used` or `Refund` changes — not on form load.

**16.** Correct flow: **Draft → Pending Approval → Approved → then** apply/refund → **Open / Closed**. Current system can skip to **Open** before steps 2–3.  
= **[Correction]** Enforce strict stage order; Open/Closed are **utilisation** stages, not **creation** stages.

**17.** **Apply Credits to Invoices** and **Create Refund Note** actions are available at `Approved || Open`. Because #14 can set **Open** early, actions may appear **before approval**.  
= **[Correction]** Gate actions on **Approved** only, or **Open** only when previously **Approved**.

---

## Shared — apply credit & refund

**18.** Apply credit correctly creates `Apply_Credit_To_Invoice_Line` and updates invoice `Amount_Due` when it runs — logic matches correct flow.  
(Timing/gating is wrong — see #9, #14, #17.)

**19.** Refund via **Create Refund Note** correctly updates `Refund` and `Credits_Remaining` on save when it runs — logic matches correct flow.  
(Same timing/gating issue.)

**20.** Validation on credit note save blocks if applied invoice has no LHDN `Invoice_UUID` — matches correct flow.  
(No correction needed.)

**21.** Deleting rows from `Credit_Applied_Invoices` on the credit note form **deletes** linked `Apply_Credit_To_Invoice_Line` and recalculates invoice balances — risky if user is not Approved yet.  
= **[Correction]** Only allow credit-application changes at **Approved+** stages; block in Draft.

---

## LHDN

**22.** LHDN submit (`Submit_Credit_Note_to_LHD1`) only runs when status is **Closed** — matches correct flow.  
(No correction needed.)

**23.** LHDN submit builds `reference_invoice_list` **only** from `Credit_Applied_Invoices` — ignores any source invoice from convert (no `Reference_Invoice` field).  
= **[Correction]** Include `Reference_Invoice` UUID in LHDN payload when set, **plus** applied invoice UUIDs.

**24.** Convert-originated credit note that is **never applied** to any invoice (only refunded, or closed another way) may submit to LHDN with **empty** reference list — even though it came from a specific invoice.  
= **[Correction]** `Reference_Invoice` from convert should always be sent to LHDN even if apply-credit step was skipped.

**25.** **Submit Credit Note to LHDN** button on the report has **no stage condition** on the button itself (only an in-script check for Closed).  
= **[Correction]** Hide/disable the button unless status is **Closed**.

**26.** Approve transition runs LHDN **taxpayer validation** (TIN, address) — matches correct flow step “LHDN taxpayer validation on Approve”.  
(No correction needed.)

---

## Summary

| Area | Items |
|---|---|
| Convert path | #1–10 |
| Manual path | #11 |
| Status / approval | #14, #16–17, #21 |
| LHDN | #23–25 |
| Aligned (no fix) | #12, #18–20, #22, #26 |
