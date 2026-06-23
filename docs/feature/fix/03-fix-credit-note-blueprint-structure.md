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
