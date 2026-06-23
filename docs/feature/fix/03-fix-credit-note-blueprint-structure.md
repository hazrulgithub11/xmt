# 03 - Fix Credit Note Blueprint Structure

## Objective
Align blueprint transition structure to target lifecycle:
`Draft -> Pending Approval -> Approved -> Open/Closed -> LHDN submit at Closed`.

## Current structural risks to address
- Utilization transitions are misaligned with credit-note timing.
- Some criteria are tied to CN LHDN fields instead of credit utilization.
- There is no explicit direct path for `Approved -> Closed` when full credit is used in one action.

## Step-by-step
1. Open blueprint: `Credit_Note_Blueprint`.
2. Keep these stages as-is:
   - `Draft`, `Pending Approval`, `Rejected`, `Approved`, `Open`, `Closed`
3. Review utilization transitions:
   - `Converted_to_Open`
   - `Converted_to_Closed`
   - `Revert_to_Pending_Approva`
4. Remove or simplify criteria that rely on CN LHDN submission fields for utilization transitions.
5. Ensure transition paths support system-driven stage updates:
   - `Approved -> Open`
   - `Approved -> Closed` (add if missing)
   - `Open -> Closed`
6. Keep approval transitions unchanged except where explicitly required:
   - `Send_For_Approval`, `Approve`, `Reject`, `Resubmit`
7. Export blueprint and verify:
   - `application/blueprints/Credit_Note_Blueprint/blueprint.json`
   - transition folders under `application/blueprints/Credit_Note_Blueprint/transitions/`
   - `XMT___Billing_System.ds`

## Zoho dependency reminder
If deleting any transition:
1. Remove all calls/assumptions from Deluge scripts first.
2. Update report action conditions that expect old stage behavior.
3. Delete transition after references are clean.

## Exit criteria
- Blueprint supports utilization stage movement from approved state.
- No transition criterion incorrectly blocks normal credit usage flow.
- Ready for workflow hardening in Step 04.

---

## Step 03 results (2026-06-23)

### Blueprint transition changes

| Transition | From → To | Change |
|---|---|---|
| `Converted_to_Open` | Approved → Open | Removed LHDN criteria (`Invoice_UUID` / `QR_Invoice_Public_Link`) — utilization no longer gated on CN submission fields |
| `Approved_to_Closed` | Approved → Closed | **Added** — supports full credit use/refund in one action via `changeStage` |
| `Converted_to_Closed` | Open → Closed | Unchanged (no criteria) |
| `Revert_to_Pending_Approva` | Approved → Pending Approval | Replaced harmful auto-criteria with `(ID == 0)` — prevents auto-revert on every approved CN missing CN LHDN UUID |

### Approval path (unchanged)
`Send_For_Approval`, `Approve` (LHDN validation script), `Reject`, `Resubmit`

### Files updated
- `application/blueprints/Credit_Note_Blueprint/blueprint.json`
- `application/blueprints/Credit_Note_Blueprint/BLUEPRINT.md`
- `application/blueprints/Credit_Note_Blueprint/transitions/Approved_to_Closed/`
- `application/blueprints/Credit_Note_Blueprint/transitions/Converted_to_Open/before/` (criteria removed)
- `application/blueprints/Credit_Note_Blueprint/transitions/Revert_to_Pending_Approva/before/phase_config.ds`
- `XMT___Billing_System.ds` (`Credit_Note_Blueprint` section)

### Deploy to live Creator
1. Open **Credit Note Blueprint** in Creator blueprint editor.
2. **Converted to Open** — remove before-transition criteria.
3. **Approved to Closed** — add transition Approved → Closed (no criteria).
4. **Revert to Pending Approval** — set criteria to `(ID == 0)` or remove auto-trigger.
5. Re-export blueprint + full app.

### Next step
Step 04 will wire `changeStage` calls in workflows to use these paths only after approval.
