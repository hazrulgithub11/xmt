# Credit Note Blueprint

- **Link name:** `Credit_Note_Blueprint`
- **Folder:** `Credit_Note_Blueprint/`
- **Form:** `Credit_Note`
- **Start stage:** `Draft`

## Stages

- Draft
- Pending Approval
- Rejected
- Approved
- Open
- Closed

## Transitions

| Transition | From | To | Scripts |
|---|---|---|---|
| [Approve](transitions/Approve/) | Pending Approval | Approved | 1 |
| [Reject](transitions/Reject/) | Pending Approval | Rejected | 0 |
| [Resubmit](transitions/Resubmit/) | Rejected | Pending Approval | 0 |
| [Send For Approval](transitions/Send_For_Approval/) | Draft | Pending Approval | 0 |
| [Converted to Open](transitions/Converted_to_Open/) | Approved | Open | 0 |
| [Approved to Closed](transitions/Approved_to_Closed/) | Approved | Closed | 0 |
| [Converted to Closed](transitions/Converted_to_Closed/) | Open | Closed | 0 |
| [Revert to Pending Approval](transitions/Revert_to_Pending_Approva/) | Approved | Pending Approval | 0 (disabled auto: `ID == 0`) |

## Folder layout

```
Credit_Note_Blueprint/
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
