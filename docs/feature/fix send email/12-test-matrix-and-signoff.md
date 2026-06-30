# 12 — Test Matrix and Sign-off (Invoice)

This is the final gate. Run after steps 01-11 pass.

## A. Core send tests

- [ ] Draft invoice cannot send
- [ ] Approved/no-credit opens Email Input Form
- [ ] Approved/no-credit first send -> email + journal + Sent/Overdue + audit
- [ ] Sent/Partially Paid/Paid/Overdue -> resend popup path only
- [ ] Resend -> no new journal, no stage change, resend audit written

## B. Notify credit tests

- [ ] Approved/credit>0 shows Notify popup
- [ ] Notify Yes -> opens Apply Credits, no immediate send
- [ ] After applying credit and sending -> net due reflected
- [ ] Notify No -> opens Email Input Form (review before send)
- [ ] Notify close/no action -> no send

## C. Data integrity tests

- [ ] Failed PDF/data fetch blocks send
- [ ] Invalid recipient blocks send
- [ ] Journal idempotency guard prevents duplicates
- [ ] Sent/resent audit fields accurate

## D. Template and output tests

- [ ] Miscellaneous invoice uses `Miscellaneous_Invoice`
- [ ] Fixed/Telephone invoice uses `Fixed_And_Telephone_Charges_Invoice`
- [ ] Email body placeholders resolved correctly

## E. Policy tests

- [ ] LHDN gate policy tested (block or warn)
- [ ] Gross invoice email does not claim unused credit was applied

## Sign-off

| Role | Name | Date | Decision | Notes |
|---|---|---|---|---|
| Finance Owner |  |  |  |  |
| Billing Ops |  |  |  |  |
| Developer |  |  |  |  |
| QA/UAT |  |  |  |  |

## Release gate

- [ ] All checks passed
- [ ] `progress_tracker.md` updated to Passed for 01-12
- [ ] Ready to implement same pattern for Debit Note (separate phase)
