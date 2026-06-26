# Step B — Retire Credit_Mode

Part of: [Unified Credit Note Rule](00-overview.md)

**Deploy only after Step A is confirmed working in production.**

Step A removed all logic that branches on `Credit_Mode`. Step B removes every remaining reference to the field and deletes it entirely so future developers have no confusion.

## Files changed in this step

1. `application/Custom Functions/credit_note/credit_mode_from_invoice_stage` — **delete**
2. `application/forms/Credit Note/workflow/Handle_reference_invoice_2.deluge`
3. `application/forms/Credit Note/workflow/Handle_Convert_Prefill.deluge`
4. `application/forms/Credit Note/workflow/Disable_Fields20.deluge`
5. `application/forms/Credit Note/Credit_Note_Report.deluge`
6. `application/forms/Credit Note/Credit_Note.deluge`
7. Creator UI — delete `Credit_Mode` field from Credit Note form **(last action)**
8. `XMT___Billing_System.ds` — mirror all above

---

## Change 1 — Delete `credit_mode_from_invoice_stage`

Delete the entire file:

```
application/Custom Functions/credit_note/credit_mode_from_invoice_stage
```

This function is no longer called anywhere after Step A (Step A removed the call in `Handle_Validation_Submiss2.deluge`) and after the changes below remove the remaining calls.

**Before deleting: confirm no remaining callers** by searching the codebase for `credit_mode_from_invoice_stage`. After Step A and the changes below, the count should be zero.

---

## Change 2 — `Handle_reference_invoice_2.deluge`

Two lines to remove:

**Line 143** — inside the ineligible branch:
```deluge
// Remove:
clear Credit_Mode;
```

**Line 148** — inside the eligible branch:
```deluge
// Remove:
input.Credit_Mode = prefill_data.get("credit_mode");
```

The `prefill_data.get("credit_mode")` call returns null after Step A's change to `prefill_from_reference_invoice`. Removing the line is clean-up.

The `credit_eligible` check and the eligibility alert on line 140–144 remain intact — they now use the direct stage check added in Step A.

---

## Change 3 — `Handle_Convert_Prefill.deluge`

**Line 133** — remove:
```deluge
// Remove:
input.Credit_Mode = prefill_data.get("credit_mode");
```

Same as above — `get("credit_mode")` already returns null after Step A.

---

## Change 4 — `Disable_Fields20.deluge`

**Line 49** — remove:
```deluge
// Remove:
disable Credit_Mode;
```

If `Disable_Fields20` disables no other fields at all after this removal, check whether the workflow itself can be deleted. Do not delete it blindly — read the full file first.

---

## Change 5 — `Credit_Note_Report.deluge`

**Line 77** — remove:
```deluge
// Remove:
Credit_Mode as "Credit Mode"
```

---

## Change 6 — `Credit_Note.deluge`

**Line 400** — remove:
```deluge
// Remove:
Credit_Mode
```

This is the field declaration in the form DSL. Removing it here prepares the export to match after the Creator UI deletion.

---

## Change 7 — Creator UI (field deletion — LAST)

1. Open Zoho Creator → XMT Billing System → Credit_Note form.
2. Go to form builder → find field `Credit_Mode`.
3. Delete the field.
4. Re-export `XMT___Billing_System.ds`.
5. Re-run form extraction scripts if applicable.

**Warning:** Deleting a field in Creator permanently drops the database column. All existing `Credit_Mode` values on historical CN records are lost. This is acceptable — the field is no longer meaningful — but confirm with the team before proceeding.

**Do not delete the field until all code changes (1–6) are deployed and verified.** If any code still reads `Credit_Mode` after field deletion, it will throw a runtime error.

---

## Pre-deletion checklist

Before executing Change 7, run this search across the full codebase. The result must be zero:

```bash
grep -r "Credit_Mode" application/
```

Expected: no matches. If any matches remain, fix them before deleting the field.

---

## Post-deploy verification

- [ ] `grep -r "Credit_Mode" application/` returns zero results
- [ ] Credit Note form in Creator has no `Credit_Mode` field
- [ ] Existing Closed/Open CNs display correctly in the CN list (no errors)
- [ ] New CN created, approved → no Credit_Mode error anywhere in Creator logs
- [ ] `credit_mode_from_invoice_stage` no longer appears in Creator custom functions list
- [ ] `XMT___Billing_System.ds` re-exported and local files match
