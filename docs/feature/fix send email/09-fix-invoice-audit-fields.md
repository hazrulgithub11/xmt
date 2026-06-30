# 09 — Invoice Audit Fields on Send

## Problem

Source invoice may not capture a reliable communication audit trail.

## Target behavior

On successful first send:

- `Sent_Date`
- `Sent_By`
- `Sent_To`
- `Send_Method`

On resend:

- `Resent_Date`
- `Resent_By`
- `Resent_To`

## Files expected to change

- `application/forms/Invoice/Invoice.deluge` (if fields missing)
- Post-send write path in send engine / hooks

## Implementation notes

- Keep field writes transactional with successful send
- Do not update sent markers when send fails

## Test Gate (must pass before step 10)

- [ ] First send writes sent audit fields
- [ ] Resend writes resend audit fields only
- [ ] Failed send writes no audit fields
- [ ] Audit values match actual recipients and operator
