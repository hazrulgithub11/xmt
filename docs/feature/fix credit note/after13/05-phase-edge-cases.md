# Phase 5 — Edge Cases and Optional Follow-Ups

Part of: [After 13 — Convert defer save](00-overview.md)

## Objective

Document edge-case handling and future enhancements. No mandatory code in this phase unless an edge case fails UAT.

---

## Edge case matrix

| Case | Expected handling | Owner phase |
|------|-------------------|-------------|
| Close popup without Submit | No CN in database | 1 + 2 |
| Remaining credit = 0 | Block at convert click; alert | 1 |
| Remaining = 500, prefill = 800 | Allow open; block on Submit if still > 500 | 1 + 4 |
| User changes `Reference_Invoice` in Draft | `Handle_reference_invoice_2` on user input re-clones | Existing |
| Double convert click | Two unsaved add forms possible; cap on save prevents over-credit | 4 |
| CN number on abandon | Not consumed until Submit | 1 + 4 |
| Orphan Draft CNs from old insert-first flow | Legacy data; no migration | N/A |
| Invoice paid between convert open and Submit | Mode locked at creation (Q21 deferred); cap still applies | 4 |
| Concurrent Draft CNs on same invoice | Both can save if each under cap individually; approve recheck catches race | 4 |
| Convert from Paid invoice (Mode B) | Prefill + Mode B; no auto-apply on approve | 2 + 4 |

---

## Workflow interaction risks

| Risk | Mitigation |
|------|------------|
| `User_Input_Trigger_Workfl2` sets Open before approval | Re-test Step 04 hardening after Phase 2 |
| `Load_Of_The_Form_during_C1` vs convert prefill order | Sandbox test supplier/customer fields |
| Full grand total stale until `User_Input_Trigger` | Toggle trigger after line insert (Phase 2) |
| URL lookup prefill fails for `Reference_Invoice` | Fallback hidden field (see Phase 2) |

---

## Optional follow-ups (not in scope)

### Lock Reference_Invoice on convert

- URL flag: `Convert_Source=1`
- On load: disable `Reference_Invoice` field when flag set
- Prevents user switching to a different invoice mid-convert

### Show remaining creditable on form

- Read-only calculated field on Credit Note form
- Step 12 optional UX — complements convert defer-save

### Partial convert without line editing

- Cap convert prefill amount to `min(invoice.Grand_Total, remaining_creditable)` at line level
- More complex; current design: user reduces qty/price in Draft

### Debit Note convert defer-save

- Same insert-first issue as Credit Note
- Separate workstream

---

## Exit criteria (Phase 5)

- [ ] Edge case matrix reviewed in UAT
- [ ] No P1 edge case failures unresolved
- [ ] Optional follow-ups logged as backlog if deferred
