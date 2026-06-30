# 01 — Preflight (Invoice Send Email Fix)

## Objective

Confirm baseline and scope before changing behavior.

## In scope

- Invoice send flow only
- Entry actions, email popup flow, journal timing, credit notify path

## Out of scope

- Debit note send flow
- Pro forma send flow
- Payment Received / Credit Note enhancements

## Checklist

- Confirm target references:
  - `overview.md`
  - `send-email-flow.md`
- Confirm affected files exist locally and match latest export:
  - `application/forms/Invoice/workflow/actions/Send_Invoice.deluge`
  - `application/forms/Invoice/workflow/actions/Send_Email5.deluge`
  - `application/forms/Email Input Form/workflow/send_email_.deluge`
  - `application/forms/Email Input Form/workflow/Handle_Load_Of_The_Form.deluge`
  - `application/forms/Notify Credits Available/workflow/Send_Invoice_To_Customer.deluge`
  - `application/forms/Notify Credits Available/workflow/Open_Form_Apply_Credit_Fo.deluge`
- Confirm finance policy decisions:
  - First-send journal on email confirm (Yes/No)
  - LHDN gate behavior (block or warn)
  - Gross-send email should not mention unused credit

## Deliverable

Preflight notes complete and blockers listed.

## Test Gate (must pass before step 02)

- [x] All in-scope files confirmed present and current (see Preflight results — one sync gap)
- [x] Policy decisions above captured (see Preflight results — LHDN pending finance)
- [ ] No unresolved blocker for step 02 — **blocked on `.ds` sync for `Send_Invoice.deluge`**

---

## Preflight results (2026-06-30)

### Reference docs

| Doc | Status |
|-----|--------|
| `overview.md` | Present — audit findings F1–F14, target state T1–T10 |
| `send-email-flow.md` | Present — invoice target flow, credit branch, first-send vs resend |

### File presence and sync vs `XMT___Billing_System.ds`

| File | Local | In `.ds` | Semantic match |
|------|-------|----------|----------------|
| `Send_Invoice.deluge` | Yes | Yes | **No — substantive drift** |
| `Send_Email5.deluge` | Yes | Yes | Yes |
| `send_email_.deluge` | Yes | Yes | Yes |
| `Handle_Load_Of_The_Form.deluge` | Yes | Yes | Yes |
| `Send_Invoice_To_Customer.deluge` | Yes | Yes | Minor — local adds `recalculate_balances_from` |
| `Open_Form_Apply_Credit_Fo.deluge` | Yes | Yes | Yes |

**`Send_Invoice.deluge` drift (action required before step 02):**

Local file has logic **not** in the current `.ds` export:

- Blueprint-gated first send: `Approved` + `Customer.Credit_Available` branching
- Journal insert on approved / no-credit path
- Notify Credits popup when `Credit_Available > 0`
- Resend branch uses stage `"paid"` (lowercase); `.ds` uses `"Paid"`

`.ds` export instead has an **unconditional** `actions` block (no Approved/credit guards) with sendmail + blueprint only — no journal, no credit notify.

**Likely cause:** local repo ahead of last `.ds` pull, or live Creator differs from export. Per double-check rule: **re-export from Creator and reconcile before implementing step 02.**

**`Send_Invoice_To_Customer.deluge` minor drift:** local line `thisapp.invoice.recalculate_balances_from(getInvoice.ID);` is absent from `.ds` (ends at `thisapp.close_form()`). Confirm which version is live.

### Baseline behavior confirmed (from code review)

| Path | Today |
|------|-------|
| `Send_Email5` | Opens Email Input Form — **no stage guard** |
| `Send_Invoice` (local) | Resend: invokeurl PDF + sendmail; Approved/no credit: journal + template PDF + stage; Approved/credit: notify popup |
| `Send_Invoice` (`.ds`) | Resend: same; other branch: template PDF + stage — **no journal, no credit gate** |
| `Send_Invoice_To_Customer` (No) | Direct sendmail + journal + stage — **bypasses email review popup** |
| `send_email_` | Email only — no journal, no stage, no audit; fires on add **and** edit |
| `Handle_Load_Of_The_Form` | Pre-fills subject/body — **does not pre-fill To** |

### Finance policy decisions

| Decision | Status | Captured value |
|----------|--------|----------------|
| First-send journal on email confirm | **Proposed (target state)** | Yes — journal created once when staff confirms send in Email Input Form (`send-email-flow.md` §2), not at `Send_Invoice` entry click. Idempotency guard required. |
| LHDN gate (`Invoice_UUID` missing) | **Pending finance sign-off** | Not enforced in send paths today. `Submit_Invoice_to_LHDN` is a separate record action. Target doc lists block **or** warn — **decision required** (step 11). |
| Gross-send email must not mention unused credit | **Proposed (target state)** | Yes — customer email shows net due only when credit was applied; gross send after notify **No** must not mention available credit (`send-email-flow.md` §1b). |

### Blockers for step 02

1. **Sync `Send_Invoice.deluge`** — reconcile local vs `XMT___Billing_System.ds` (and live Creator) before editing entry gate.
2. **LHDN policy** — does not block step 02 (remove Send Email button) but blocks step 11 and full UAT sign-off.

### Non-blockers (confirmed in scope)

- Invoice send flow only; debit note / pro forma / payment received out of scope per checklist.
- All six target files exist locally; five of six match `.ds` semantically (one minor line on notify No-path).
