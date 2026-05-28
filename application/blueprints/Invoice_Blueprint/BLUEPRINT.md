# Invoice Blueprint

- **Link name:** `Invoice_Blueprint`
- **Folder:** `Invoice_Blueprint/`
- **Form:** `Invoice`
- **Start stage:** `Draft`

## Stages

- Draft
- Pending Approval
- Rejected
- Approved
- Sent
- Partially Paid
- Paid
- Overdue

## Transitions

| Transition | From | To | Scripts |
|---|---|---|---|
| [Approve](transitions/Approve/) | Pending Approval | Approved | 1 |
| [Reject](transitions/Reject/) | Pending Approval | Rejected | 1 |
| [Resubmit](transitions/Resubmit/) | Rejected | Pending Approval | 1 |
| [Send For Approval](transitions/Send_For_Approval/) | Draft | Pending Approval | 1 |
| [Send Invoice](transitions/Send_Invoice/) | Approved | Sent | 1 |
| [Payment Received Partial from Sent](transitions/Payment_Received_Partial1/) | Sent | Partially Paid | 0 |
| [Payment Received Full from Sent](transitions/Payment_Received_Full_fro2/) | Sent | Paid | 0 |
| [Due Date Passed from Sent](transitions/Due_Date_Passed_from_Sent/) | Sent | Overdue | 0 |
| [Payment Received Full from Partially Paid](transitions/Payment_Received_Full_fro1/) | Partially Paid | Paid | 0 |
| [Payment Received Full from Overdue](transitions/Payment_Received_Full_fro/) | Overdue | Paid | 0 |
| [Due Date Passed from Partially Paid](transitions/Due_Date_Passed_from_Part/) | Partially Paid | Overdue | 0 |
| [Partially Paid to Sent](transitions/Partially_Paid_to_Sent/) | Partially Paid | Sent | 0 |
| [Paid to Sent](transitions/Paid_to_Sent/) | Paid | Sent | 0 |
| [Overdue to Sent](transitions/Overdue_to_Sent/) | Overdue | Sent | 0 |
| [Revert to Pending Approval](transitions/Revert_to_Pending_Approva/) | Approved | Pending Approval | 0 |

## Folder layout

```
Invoice_Blueprint/
  BLUEPRINT.md          ← this file
  blueprint.json        ← machine-readable metadata
  transitions/
    <TransitionLinkName>/
      transition.json
      before|during|after/
        unconditional/  or  if_<condition>/
          script_01.deluge
          CONDITION.txt   (if conditional)
```

Source: `XMT___Billing_System.ds` (blueprint section).
Re-run `python3 scripts/extract_blueprints.py` after exporting from Zoho.
