# Credit Note — Correct End-to-End Flow

## 1. Credit Note from Invoice (Convert)

```mermaid
flowchart TD
    A[Invoice: Sent / Partially Paid / Paid / Overdue] --> B{User clicks Convert to Credit Note}
    B --> C[System creates Credit Note]

    C --> C1[Copy supplier + customer + lines + totals]
    C --> C2[Set Reference_Invoice = source invoice]
    C --> C3[Generate CN number once]
    C --> C4[Set Credits_Used=0, Refund=0, Credits_Remaining=Grand_Total]
    C --> C5[Blueprint = Draft]

    C5 --> D[User reviews in Credit Note form]
    D --> E{Adjust amount?}
    E -->|Full credit| F[Keep all lines]
    E -->|Partial credit| G[Reduce qty / remove lines / edit amounts]
    F --> H[Save Draft]
    G --> H

    H --> I[Send for Approval]
    I --> J[Pending Approval]
    J --> K{Approver}
    K -->|Reject| L[Rejected → fix → Resubmit]
    L --> J
    K -->|Approve| M[LHDN taxpayer validation]
    M -->|Fail| J
    M -->|Pass| N[Approved]

    N --> O{How is credit used?}

    O -->|Customer not paid / partial paid| P[Apply Credits to Invoices]
    P --> P1[Prefer apply to Reference_Invoice first]
    P1 --> P2[Create Apply_Credit_To_Invoice_Line]
    P2 --> P3[Update Invoice: Credits_Applied_Total + Amount_Due]
    P3 --> P4[Update CN: Credits_Used + Credits_Remaining]

    O -->|Customer already paid| Q{Choice}
    Q -->|Offset future bill| P
    Q -->|Cash back| R[Create Refund Note from CN]
    R --> R1[Refund Note approved + paid]
    R1 --> R2[Update CN: Refund + Credits_Remaining]

    P4 --> S{Credits_Remaining?}
    R2 --> S
    S -->|> 0| T[Blueprint = Open]
    S -->|= 0| U[Blueprint = Closed]

    T --> O
    U --> V[Submit Credit Note to LHDN]
    V --> V1[Include reference invoice UUID from Reference_Invoice and/or applied invoices]
    V1 --> W[Store Invoice_UUID + public link]
    W --> X[Done]
```

## 2. Credit Note from Credit Notes Module (Manual)

```mermaid
flowchart TD
    A[Credit Notes report → Add] --> B[Form loads]
    B --> B1[Prefill supplier from Organization Settings]
    B --> B2[User picks Customer + Charge Category]

    B2 --> C[User adds line items]
    C --> C1[Monthly Rental / Internet / Call Charges]
    C --> C2[System calculates tax + Grand_Total]
    C --> C3["No Reference_Invoice at creation — OK for promo / standalone"]

    C3 --> D[Save]
    D --> D1[Generate CN number once]
    D1 --> D2[Blueprint = Draft]
    D2 --> D3[Credits_Remaining = Grand_Total]

    D3 --> E[Send for Approval]
    E --> F[Pending Approval]
    F --> G{Approver}
    G -->|Reject| H[Rejected → fix → Resubmit]
    H --> F
    G -->|Approve| I[LHDN taxpayer validation]
    I -->|Fail| F
    I -->|Pass| J[Approved]

    J --> K{Credit type?}

    K -->|Promo / goodwill| L{Customer choice}
    L -->|Wait for next bill| M[Hold as Open credit]
    M --> N[Apply Credits when next invoice exists]
    L -->|Want cash now| O[Create Refund Note]
    O --> P[CN Closed when fully refunded]

    K -->|Correction not tied to one invoice yet| N

    N --> N1[Apply Credits to Invoices popup]
    N1 --> N2["Pick customer's open invoice(s)"]
    N2 --> N3[Create Apply_Credit_To_Invoice_Line]
    N3 --> N4[Update Invoice Amount_Due]
    N4 --> N5[Update CN balances]

    N5 --> Q{Credits_Remaining?}
    P --> Q
    Q -->|> 0| R[Blueprint = Open]
    Q -->|= 0| S[Blueprint = Closed]

    R --> K
    S --> T[Submit Credit Note to LHDN]
    T --> T1{Any invoice applied?}
    T1 -->|Yes| T2["Reference = applied invoice UUID(s)"]
    T1 -->|"No — pure promo refund only"| T3["Standalone CN — no invoice reference"]
    T2 --> U[Store UUID + public link]
    T3 --> U
    U --> V[Done]
```

## 3. Entry Points — Where They Differ vs Merge

```mermaid
flowchart LR
    subgraph ENTRY["Entry points"]
        INV[Invoice → Convert]
        MAN[Credit Notes → Add]
    end

    subgraph DIFF["Only difference at start"]
        INV --> INV1[Prefilled from invoice]
        INV --> INV2[Reference_Invoice = source invoice]
        MAN --> MAN1[User enters customer + lines]
        MAN --> MAN2[Reference_Invoice = empty OK]
    end

    subgraph SHARED["Same from here onward"]
        S1[Draft]
        S2[Pending Approval → Approved]
        S3[Apply credit OR Refund]
        S4[Open / Closed by Credits_Remaining]
        S5[LHDN submit when Closed]
    end

    INV2 --> S1
    MAN2 --> S1
    S1 --> S2 --> S3 --> S4 --> S5
```

## 4. Balance Logic (Both Paths)

```mermaid
flowchart LR
    GT[Grand_Total] --> CR[Credits_Remaining]
    CU[Credits_Used — applied to invoices] --> CR
    RF[Refund — via Refund Note] --> CR

    CR -->|Grand_Total - Credits_Used - Refund| CR

    CR -->|"> 0"| OPEN[Status: Open]
    CR -->|"= 0"| CLOSED[Status: Closed → LHDN eligible]
```
