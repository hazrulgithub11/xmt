# XMT Billing System — Blueprints

## What is a Blueprint?

In Zoho Creator, a **Blueprint** is a visual state machine on a form. Records move
through **stages** (e.g. Draft → Pending Approval → Approved → Sent). Users or
automation trigger **transitions** to change stage.

Each transition has up to three execution phases:

| Phase | When it runs | Typical use in this app |
|---|---|---|
| **Before** | Before the transition | Permissions, confirm dialogs |
| **During** | While collecting input | Show fields (e.g. rejection reason) |
| **After** | After stage change | Email, LHDN submit, journal entries, `changeStage` |

After-phase actions can be **unconditional** or run only when a **criteria**
expression is true (e.g. `Customer.Credit_Available > 0` on Send Invoice).

## This repo layout

```
application/blueprints/
  <BlueprintLinkName>/
    BLUEPRINT.md              # human overview + transition table
    blueprint.json            # full metadata (for tooling)
    transitions/<Transition>/
      transition.json
      before/phase_config.ds  # owners, confirmations (if any)
      during/phase_config.ds
      after/unconditional/script_01.deluge
      after/if_<criteria>/CONDITION.txt
```

Scripts here are extracted from `XMT___Billing_System.ds`. Related logic also
lives in form workflows, schedules, and custom functions that call:
`thisapp.blueprint.executeTransition(...)` or `thisapp.blueprint.changeStage(...)`.

## Extracted blueprints

| Blueprint | Form | Transitions | Deluge scripts |
|---|---|---:|---:|
| [Credit_Note_Blueprint](Credit_Note_Blueprint/BLUEPRINT.md) | Credit_Note | 7 | 0 |
| [Invoice_Blueprint](Invoice_Blueprint/BLUEPRINT.md) | Invoice | 15 | 5 |
| [Deposits_Blueprint](pro forma invoice/BLUEPRINT.md) | Pro_Forma_Invoices | 15 | 6 |
| [Debit_Note_Blueprint](Debit_Note_Blueprint/BLUEPRINT.md) | Debit_Note | 15 | 5 |

## Invoice Blueprint (largest)

Stages: Draft → Pending Approval → Approved → Sent → Partially Paid / Paid / Overdue,
with Rejected and Resubmit loop. Heavy scripts on **Approve** (LHDN, journals,
balance) and **Send Invoice** (stage routing + credit popup). Payment transitions
are often driven from **Payment Received** workflows via `changeStage`, not only
from the blueprint UI.

## Regenerate from export

```bash
python3 scripts/extract_blueprints.py
```

## Zoho references

- [Creator Blueprint tasks (Deluge)](https://www.zoho.com/deluge/help/creator-blueprint-tasks.html)
- [Execute transition](https://www.zoho.com/deluge/help/creator-blueprint-tasks/execute-transition.html)
- [Blueprint attributes](https://www.zoho.com/deluge/help/creator-blueprint-tasks/blueprint-attributes.html)
