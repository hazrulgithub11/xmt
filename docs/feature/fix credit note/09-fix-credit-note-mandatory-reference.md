# 09 - Make Reference_Invoice Mandatory at Creation

## Context
Step 02 added `Reference_Invoice` as an **optional** field to support standalone/promo manual CNs.
The new flow (`creditNote_Flow.md`) removes standalone CNs entirely. Every credit note — manual or converted — must link to an LHDN-validated invoice before it can be saved.

**This step supersedes the "Required: No" decision from Step 02.**

## Objective
Block any credit note save that has no `Reference_Invoice`, and ensure the referenced invoice already holds a valid `Invoice_UUID` from LHDN.

## Why this is safe to do now
- Steps 02–07 are complete. `Reference_Invoice` field exists on the form.
- Convert path (Step 05) already sets `Reference_Invoice` automatically.
- The only gap is manual creation, which currently allows saving without picking a reference invoice.

## Primary files
- `application/forms/Credit Note/Credit_Note.deluge` — form field required flag
- `application/forms/Credit Note/workflow/Handle_reference_invoice_2.deluge` — existing UUID validator
- `application/forms/Credit Note/workflow/Handle_Validation_Submiss2.deluge` — save/submit guard (`on validate`)

## Dependency
Step 02 must already be deployed (field exists). Steps 03–07 should be deployed first so the form is stable before adding this hard block.

---

## Step-by-step

### 1. Change the form field to required

In `Credit_Note.deluge` (and in Creator UI), change `Reference_Invoice` lookup:

```
Reference_Invoice
  required = true
```

**Note:** In Zoho Creator, a lookup field marked required blocks form submission if empty. This alone enforces selection.

### 2. Add a save-time guard for UUID presence

The existing `Handle_reference_invoice_2.deluge` already validates UUID on **field selection**. Add a matching guard in `Handle_Validation_Submiss2.deluge` (`on validate`) so that a CN cannot be saved if the linked invoice lacks `Invoice_UUID`:

```deluge
if(input.Reference_Invoice != null)
{
    ref_uuid = input.Reference_Invoice.Invoice_UUID;
    if(ref_uuid == null || ref_uuid == "")
    {
        alert("Reference Invoice does not have a valid LHDN UUID. Submit the invoice to LHDN first, then create the credit note.");
        cancel submit;
    }
}
else
{
    // Reference_Invoice is null — block save (field required rule is first guard)
    alert("A Credit Note must be linked to a reference invoice. Please select a Reference_Invoice.");
    cancel submit;
}
```

### 3. Convert path — verify already set (optional)

`Convert_To_Credit_Note.deluge` (Step 05) already does:

```deluge
Reference_Invoice = input.ID
```

**Optional** pre-convert guard — only if you need to block convert before insert (record actions often cannot use `alert`; use `openUrl` to `Alert_Message` or a report `condition` on the button instead):

```deluge
if(input.Invoice_UUID == null || input.Invoice_UUID == "")
{
    openUrl("#Form:Alert_Message?Error_Message=" + zoho.encryption.urlEncode("This invoice has not been submitted to LHDN yet. Submit it to LHDN first before creating a Credit Note."),"popup window","height=auto,width=auto");
    return;
}
```

**Deployed (Step 09):** Skipped. Convert button is already limited to `Sent` / `Partially Paid` / `Paid` / `Overdue`; in practice those invoices should already be LHDN-submitted. Any CN created without UUID is still blocked on the next manual save via Step 2.

### 4. Update `Handle_reference_invoice_2.deluge` message (optional)

The existing workflow already clears the field if UUID is missing. Message tweak is cosmetic only.

**Deployed (Step 09):** Skipped — existing alert is sufficient.

### 5. Remove null-reference tolerance in action guards

In `Handle_Credit_Note_Select1.deluge` (Apply Credit To Invoices picker init), the existing code tolerates `Reference_Invoice = null`. After this step, `Reference_Invoice` will always be set. No code change needed here, but confirm behaviour still works when it is always populated.

### 6. Update form layout note

If a "Reference Invoice" section shows "(optional)" label text anywhere in the Creator form layout, remove that label.

---

## Zoho safety

- Changing a field from optional to required in Creator **does not break existing records** — it only blocks new submissions.
- Existing CNs with `Reference_Invoice = null` (created before this step) remain unaffected until edited. Consider a one-time cleanup script if needed.

## Exit criteria

- [x] Manual Credit Note → Add → Save without picking `Reference_Invoice` → **blocked with message**
- [x] Manual Credit Note → Add → Pick invoice with no `Invoice_UUID` → **blocked with message**
- [x] Manual Credit Note → Add → Pick LHDN-validated invoice → **allowed, saves as Draft**
- [ ] Convert from unsubmitted invoice → **not blocked at convert** (skipped; mitigated by invoice stage + save guard on edit)
- [x] Convert from LHDN-validated invoice → **allowed**
- [x] Existing CNs with null `Reference_Invoice` are not broken on open/edit (read-only path only)
- [ ] `Credit_Note.deluge` and `XMT___Billing_System.ds` synced after deploy
