# som_mae_financials — Financial Constants

This file holds audited financial constants and historical benchmarks.
These numbers do NOT change between QuickBooks export runs — they come from
audited financial statements and the T2 tax return filed each October.

Read this file only when answering ad-hoc questions about history or tax.
**Do not read this file during a standard "Regenerate all reports" run.**

---

## Current Fiscal Year (FY2025-26)

| Item | Value |
|---|---|
| Period | Aug 1, 2025 – Jul 31, 2026 |
| Expected students | ~950 |
| Expected gross revenue | ~$3.2M CAD (YTD extrapolation projects ~$3.36M as of Feb 2026) |
| Required marketing spend (3%) | ~$96,000–$101,000 |

---

## Revenue & Income — Key Benchmarks

| Item | Value | Source |
|---|---|---|
| FY2024-25 full-year tuition | $3,020,723 | FY2024-25 audited financials |
| FY2024-25 YTD tuition (Aug 1 – Feb 20, 2025) | $1,939,304 | QuickBooks comparison column |
| YTD-to-annual ratio | 64.2% | Derived from above |
| FY2024-25 accounting income before tax | $310,894 | FY2024-25 audited financials |
| FY2024-25 taxable income (CRA basis) | $308,658 | T2 return, line 360 |
| Difference (accounting vs. taxable) | −$2,236 | Very small — books closely match tax |

---

## Tax — FY2024-25 (confirmed from T2)

| Item | Value | Source |
|---|---|---|
| Federal Part I tax | $31,350 | T2 line 700 |
| Ontario provincial tax | $10,876 | T2 Schedule 500 |
| Total tax payable | $42,226 | T2 line 770 |
| Effective tax rate | 13.68% | T2 summary |
| SBD business limit | $300,000 | T2 line 410 — each business gets $300,000 separately |
| Income taxed at small business rate | $296,622 | T2 line 400 (active business income) |

---

## FY2025-26 Installment Schedule (from T2 cover letter by Tang & Partners)

| Due Date | Amount |
|---|---|
| October 31, 2025 | $1,530 |
| January 31, 2026 | $13,565 |
| April 30, 2026 | $13,565 |
| July 31, 2026 | $13,566 |
| **Total FY2025-26 installments** | **$42,226** |
| October 31, 2026 (first installment FY2026-27) | $10,557 |

---

## Capital Cost Allowance (CCA) — Tax Depreciation

CCA is the amount the government lets you deduct from income each year for assets you've bought.
It follows fixed rates per "class" (category) set by CRA, not the same as your accounting books.

| CCA Class | What It Is | UCC Start FY2024-25 | FY2024-25 CCA | UCC Start FY2025-26 | FY2025-26 CCA (est.) |
|---|---|---|---|---|---|
| Class 13-a | Leasehold improvements (main) — lease EXPIRED Jul 31 2025 | $79,408 | $79,408 | $0 | $0 |
| Class 13-b | Leasehold improvements (secondary) | $9,000 | ~$900 | ~$8,100 | ~$1,700 |
| Class 8 | Furniture & fixtures (20% declining) | $15,539 | $3,108 | $12,431 | $2,486 |
| Class 14.1 | Franchise fee (5% declining) | $18,686 | $934 | $17,752 | $888 |
| Class 50 | Computer equipment (55% declining) | $2,493 | $2,718 | $4,673 | $2,570 |
| **Total** | | **$125,126** | **~$87,068** | **~$42,956** | **~$7,644** |

The leasehold improvement lease (Class 13-a) expired on July 31, 2025. This was the biggest
annual CCA deduction ($79,408/year). Now that it is gone, the company will have ~$79,000 less
in tax deductions each year — which is the main reason taxes are rising.

---

## 3-Year Aggregate Benchmarks (Aug 2022 – Jul 2025)

| Item | 3-Year Total | Annual Average |
|---|---|---|
| Tuition (gross) | $8,540,593 | $2,846,864 |
| Total payroll (all 5200 accounts) | $4,470,987 | $1,490,329 |
| Marketing & advertising (all 6200 accounts) | $269,181 | $89,727 |
| FTC charges (account 6201.1) | $72,175 | $24,058 |
| IT expenses (all 6405 accounts) | $418,151 | $139,384 |
| Amortization / depreciation | $278,511 | $92,837 |

---

## Other Constants

| Item | Value | Source |
|---|---|---|
| GIC balance | $700,000 | FY2024-25 balance sheet |
| Franchise royalty rate | 12% of gross revenue | Franchise agreement |
| Marketing obligation | 3% of gross revenue | Franchise agreement |
| 3-year avg marketing spend | $89,727/year | 3-year P&L |
| 3-year avg FTC charges | $24,058/year | 3-year P&L (currently $0 in FY2025-26) |

---

## How to Read Source Files (for script writing only)

These snippets are for reference when writing new scripts. They are NOT needed for report runs.

### Excel files (QuickBooks exports)

```python
import openpyxl
wb = openpyxl.load_workbook('data/current/Profit and Loss - Compare YTD for 3 years.xlsx', data_only=True)
ws = wb['Sheet1']
for row in ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=True):
    if any(c is not None for c in row):
        print(row)
```

The spreadsheet header (rows 1–5) contains the report title and the three YTD periods being compared.
Always read the header to determine the exact YTD cutoff date — do NOT assume it matches a prior report.

### PDF financial statements

```python
import pdfplumber
with pdfplumber.open('data/archive/FinancialStatement_2039321 ONTARIO INC_2024-2025.pdf') as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            print(text)
```

Key pages: Balance Sheet, Statement of Income and Retained Earnings, Notes.

**T2 reading tip:** The T2 PDF has 73 pages. Write extracted text to a file first, then search
for key terms. Critical sections: `Schedule 100` (Balance Sheet), `Schedule 125` (Income Statement),
`Undepreciated capital cost` (CCA / Schedule 8), `T2 Summary`, `Schedule 500` (Ontario tax).

### Background doc (python-docx)

```python
from docx import Document
doc = Document('docs/MAE-background and requirements.docx')
for para in doc.paragraphs:
    if para.text.strip():
        print(para.text)
```
