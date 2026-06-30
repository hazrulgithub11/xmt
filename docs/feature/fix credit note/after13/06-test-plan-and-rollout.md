# Phase 6 — Test Plan, Rollout, and Sign-Off

Part of: [After 13 — Convert defer save](00-overview.md)

## Zoho safety (pre-UAT)

- [ ] URL param `Reference_Invoice={id}` prefills lookup on Credit Note **add** form (sandbox)
- [ ] Subform `insert` works on add form load (not only edit)
- [ ] Workflow order: `Load_Of_The_Form_during_C1`, convert prefill, `Load_of_the_form_Initiali1` — no Open promotion before Submit
- [ ] Fallback documented if lookup URL prefill fails (`Convert_Source_Invoice_ID` hidden field)

---

## Test matrix

Use sandbox / test customer. Record invoice ID and CN ID per row.

| # | Scenario | Steps | Expected | Pass |
|---|----------|-------|----------|------|
| T16-1 | Convert with remaining credit | Invoice with RM 500 remaining → Convert | Add popup; **Submit** button; CN **not** in list | [ ] |
| T16-2 | Abandon convert | Convert → close without Submit | No new CN in Credit Notes report | [ ] |
| T16-3 | Convert partial save | Convert → edit to RM 500 → Submit | Draft CN; `Grand_Total` = 500 | [ ] |
| T16-4 | Convert over cap at save | Convert → leave RM 800 → Submit | Blocked — cumulative cap message | [ ] |
| T16-5 | Convert zero remaining | Fully credited invoice → Convert | Alert at click; no popup | [ ] |
| T16-6 | Manual add regression | Add CN → pick reference | Unchanged from pre-change behavior | [ ] |
| T16-7 | Convert Mode A | Convert from Sent invoice | `Credit_Mode` = Mode A; lines cloned | [ ] |
| T16-8 | Convert Mode B | Convert from Partially Paid invoice | `Credit_Mode` = Mode B; lines cloned | [ ] |
| T16-9 | Approve converted CN | T16-3 CN → Send → Approve | Cap recheck; Mode A/B path correct | [ ] |
| T16-10 | CN number timing | Convert → do not Submit → check list | No CN number consumed; no list row | [ ] |
| T16-11 | CN number on submit | After T16-3 Submit | Exactly one `Invoice_No` assigned | [ ] |

---

## Deploy order

| Order | Artifact | Phase |
|-------|----------|-------|
| 1 | `Handle_Convert_Prefill.deluge` (or extended on-load workflow) | 2 |
| 2 | `Convert_To_Credit_Note.deluge` | 1 |
| 3 | `prefill_from_reference_invoice` custom function + refactored callers | 3 (optional same batch) |
| 4 | Re-export `XMT___Billing_System.ds` | All |

**Important:** Deploy Phase 2 **before or together with** Phase 1. Phase 1 alone opens an empty add form.

---

## Exit criteria (full workstream)

- [ ] Convert does not call `insert into Credit_Note` before opening the form
- [ ] Add form opens with **Submit** (not **Update**)
- [ ] Closing without Submit leaves no CN record
- [ ] Lines and `Credit_Mode` prefilled from source invoice
- [ ] Cap enforced on Submit and Approve (unchanged behavior)
- [ ] All touched files synced to `XMT___Billing_System.ds`
- [ ] T16-1 to T16-11 passed in Creator sandbox

---

## Rollback

| Step | Action |
|------|--------|
| 1 | Restore `Convert_To_Credit_Note.deluge` to insert-then-`recLinkID` version |
| 2 | Disable or remove convert on-load prefill workflow |
| 3 | If Phase 3 shipped: revert `Handle_reference_invoice_2` to inline clone OR keep function if manual path depends on it |

No data migration required. Orphan Draft CNs created under old flow remain in the system.

---

## Post-deploy sign-off

| Item | Owner | Date | Done |
|------|-------|------|------|
| Phase 1 + 2 deployed to sandbox | | | [ ] |
| T16-1 – T16-11 passed | | | [ ] |
| Phase 3 deployed (if deferred) | | | [ ] |
| Production deploy | | | [ ] |
| Post-deploy export committed | | | [ ] |
