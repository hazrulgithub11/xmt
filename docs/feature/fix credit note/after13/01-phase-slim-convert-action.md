# Phase 1 — Slim Down `Convert_To_Credit_Note.deluge`

Part of: [After 13 — Convert defer save](00-overview.md)

## Objective

Remove database insert from the convert record action. On button click, run **validation only**, then open the Credit Note **add** form with minimal URL prefill params.

## Primary file

- `application/forms/Invoice/workflow/actions/Convert_To_Credit_Note.deluge`

## Dependency

- Cumulative cap hotfix deployed (convert blocks when `remaining_creditable <= 0`).
- Phase 2 must be deployed **before or with** Phase 1 in production — otherwise convert opens an empty add form.

---

## Keep (pre-click validation only)

| Check | Rule |
|-------|------|
| Invoice stage | Sent, Overdue, Partially Paid, or Paid |
| Remaining credit | `remaining_creditable <= 0` → alert, no popup |
| LHDN readiness (light) | `Invoice_UUID` present on source invoice (align Step 09; full validation on Submit) |

**Remaining credit formula** (same as Step 12 hotfix):

```
crediting_cn_list = Credit_Note[Reference_Invoice == ref_invoice_id
  && (Blueprint.Current_Stage == "Approved"
   || Blueprint.Current_Stage == "Closed"
   || Blueprint.Current_Stage == "Open"
   || Blueprint.Current_Stage == "Pending Approval")]

remaining_creditable = Invoice.Grand_Total - SUM(crediting_cn_list.Grand_Total)
```

Block convert only when `remaining_creditable <= 0` — **not** when full invoice amount > remaining (user edits on Submit).

---

## Remove (~170 lines)

- `insert into Credit_Note` and entire field map.
- All subform line inserts (`Monthly_Rental`, `Internet_Charges`, `Call_Charges`).
- `Invoice_No = thisapp.credit_note.generate_credit_note_no()` at convert time.
- `try/catch` around insert and row-count rollback delete logic.

CN number generation stays on first **Submit** via `Handle_Invoice_Creation1.deluge`.

---

## Replace open URL

**Before:**

```deluge
openURL("#Form:Credit_Note?recLinkID=" + create_credit_note_id + "&viewLinkName=Credit_Notes", "popup window");
```

**After:**

```deluge
openURL("#Form:Credit_Note?viewLinkName=Credit_Notes&Reference_Invoice=" + input.ID + "&Customer=" + input.Customer, "popup window");
```

- **No `recLinkID`** — add mode, not edit.
- Pass **minimal** params; Phase 2 loads header + lines in `on load`.
- Same pattern as Create Refund Note (`Reference_Credit_Note=...&Customer=...`).

---

## Error handling

Keep existing `errorMessage` → `Alert_Message` popup for:

- Ineligible invoice stage
- No remaining creditable amount
- Missing `Invoice_UUID` (if added in this phase)

On success: open Credit Note add form (no success message required, or brief toast if preferred).

---

## Exit criteria (Phase 1)

- [x] `Convert_To_Credit_Note.deluge` contains no `insert into Credit_Note`
- [x] Convert opens `#Form:Credit_Note` without `recLinkID`
- [x] Convert still blocks when `remaining_creditable <= 0`
- [x] Convert does **not** block when full invoice amount > remaining (that is Submit’s job)
- [~] Synced to `XMT___Billing_System.ds`

---

## Deploy note

**Do not deploy Phase 1 alone to production** without Phase 2 — users would get an add form with only `Reference_Invoice` / `Customer` set and no lines until Phase 2 is live.
