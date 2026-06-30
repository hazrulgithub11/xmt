# Phase 4 — Save and Approval Path (Verification Only)

Part of: [After 13 — Convert defer save](00-overview.md)

## Objective

Confirm Phases 1–2 do **not** require changes to existing save, numbering, or approval logic. Document expected behavior for QA.

## Primary files (no code changes expected)

| File | Role |
|------|------|
| `application/forms/Credit Note/workflow/Handle_Validation_Submiss2.deluge` | `on validate` — cap, lines, reference, UUID |
| `application/forms/Credit Note/workflow/Handle_Invoice_Creation1.deluge` | `on add` success — generate `Invoice_No` once |
| `application/forms/Credit Note/workflow/Handle_Submission_Form_an4.deluge` | `on success` — stage transitions (Draft only until approval) |
| `application/blueprints/Credit_Note_Blueprint/transitions/Approve/after/unconditional/script_01.deluge` | Cap recheck + LHDN + Mode A auto-apply |

---

## Expected behavior after Phases 1–2

### On Submit (add — first save)

1. `Handle_Validation_Submiss2` runs:
   - Mandatory `Reference_Invoice` + LHDN UUID
   - Per-line reduce-only vs source invoice
   - Cumulative cap (counts Approved + Closed + Open + Pending Approval)
   - `Credit_Mode` set
2. Record inserted → blueprint **Draft**
3. `Handle_Invoice_Creation1` assigns `Invoice_No` if empty

### On Submit (edit — subsequent saves)

Same validation; cap uses `cn_grand_total` from line sums.

### On Approve

1. Cumulative cap recheck in `script_01`
2. LHDN taxpayer validation
3. Mode A → auto-apply + Closed (Step 13)
4. Mode B → stays Approved/Open until apply/refund

---

## User journey (end-to-end)

```
Convert click     → validate only, open add form (Phase 1)
Form load         → prefill 800 (Phase 2)
User edits to 500 → still unsaved
Submit            → validate passes → Draft CN created, CN number assigned
Send / Approve    → existing blueprint flow
```

```
Convert click     → prefill 800
Submit at 800     → validate FAIL (remaining 500) → no save
```

---

## Regression checks

| Area | Verify |
|------|--------|
| Manual Add + pick reference | Unchanged |
| Cap at save | Still blocks over-limit amounts |
| Cap at approve | Still rechecks concurrent CNs |
| Mode A auto-apply | Still runs on approve for Sent/Overdue ref at creation |
| CN numbering | Once per record, on first add success only |

---

## Exit criteria (Phase 4)

- [ ] No unintended edits to validation / creation / approve scripts
- [ ] Smoke test: converted CN can complete Draft → Pending → Approved → Closed/Open
- [ ] T16-3, T16-4, T16-9 pass (see [06-test-plan-and-rollout.md](06-test-plan-and-rollout.md))
