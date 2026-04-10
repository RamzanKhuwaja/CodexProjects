# som_vau_financials — Financial Constants

This file holds audited financial constants and historical benchmarks.
These numbers do NOT change between QuickBooks export runs — they come from
reviewed financial statements and the T2 tax return filed each October.

Read this file only when answering ad-hoc questions about history or tax.
**Do not read this file during a standard "Regenerate all reports" run.**

---

## Current Fiscal Year (FY2025-26)

| Item | Value |
|---|---|
| Period | Aug 1, 2025 – Jul 31, 2026 |
| Year of operation | 16th year |

---

## Revenue & Income — Key Benchmarks

| Item | Value | Source |
|---|---|---|
| FY2024-25 full-year tuition | $2,038,228 | FY2024-25 reviewed financials |
| FY2024-25 net income before tax | $522,393 | FY2024-25 reviewed financials |
| FY2023-24 full-year tuition | $1,878,225 | FY2023-24 reviewed financials |
| FY2025-26 YTD / projection figures | Read from the current QuickBooks export each session | QuickBooks |

---

## Tax — FY2024-25 (confirmed from T2)

| Item | Value | Source |
|---|---|---|
| Net income for tax purposes (line 300) | $515,851 | T2 return |
| Taxable income (line 360) | $490,652 | T2 return |
| Federal Part I tax (line 700) | $63,508 | T2 return |
| Ontario provincial tax (Schedule 500) | $39,825 | T2 return |
| Part IV tax | $3,795 | T2 return |
| Total tax payable (line 770) | $107,128 | T2 return |
| Dividend refund | $5,337 | T2 return |
| Balance owing (after dividend refund) | $101,791 | T2 return / Balance sheet |
| Effective rate (Part I only) | 12.94% | T2 summary |
| Effective total rate (all taxes) | 21.83% | T2 summary |
| Active business income | $493,616 | T2 summary |
| Small business deduction | $38,000 | T2 return |

**Note on FY2024-25 taxes:** The high effective rate (21.83% overall) includes Part IV tax on
investment income from the IG Wealth Management portfolio. The core business tax rate (12.94%)
is within the normal range for a small Canadian corporation.

---

## Capital Cost Allowance (CCA) — Tax Depreciation

CCA is the amount the government lets you deduct from income each year for assets you've bought.

| CCA Class | What It Is | Net Book Value Jul 31, 2025 | FY2025-26 CCA (est.) |
|---|---|---|---|
| Class 13-a | Leasehold improvements (expires ~Jul 2027) | $37,245 | ~$33,783 |
| Class 8-a | Furniture & fixtures (20% declining) | $9,453 | ~$1,891 |
| Class 50-a | Computer equipment (55% declining) | $5,268 | ~$2,897 |
| Class 14.1-a | Franchise fee (5% declining) | $13,778 | ~$689 |
| **Total** | | **$65,744** | **~$39,260** |

The leasehold improvements (Class 13-a) are amortized straight-line over 10 years from 2017,
so they expire around July 2027. Approximately 2 more years of ~$33,783/yr deduction remaining.

---

## 3-Year Aggregate Benchmarks (Aug 2022 – Jul 2025)

| Item | 3-Year Total | Annual Average |
|---|---|---|
| Tuition (gross) | $5,866,752 | $1,955,584 |
| Total payroll (all 5200 accounts) | $2,084,485 | $694,828 |
| Marketing & advertising (all 6200 accounts) | $190,710 | $63,570 |
| FTC charges (6201.2) | $74,202 | $24,734 |
| IT expenses (all 6405 accounts) | $353,692 | $117,897 |
| Amortization / depreciation | $146,882 | $48,961 |
| Student Handouts (5780) | $197,885 | $65,962 |

---

## Other Constants

| Item | Value | Source |
|---|---|---|
| Short-term investments (IG Wealth) | $2,355,061 | FY2024-25 balance sheet |
| Retained earnings | $1,834,688 | FY2024-25 balance sheet |
| Franchise royalty rate | 22% of gross revenue | Franchise agreement |
| Marketing obligation | 3% of gross revenue | Franchise agreement |
| Franchise agreement expiry | 2027 | Notes to financial statements |
| Campus address | 9135 Keele Street, Unit B3/B4 | Lease (5605) |
| SBD limit | $300,000 | Confirmed — each business gets $300K separately |

---

## How to Read Source Files (for script writing only)

These snippets are for reference when writing new scripts. They are NOT needed for report runs.

### Excel files (QuickBooks exports)

```python
import openpyxl
wb = openpyxl.load_workbook('data/current/<filename>.xlsx', data_only=True)
ws = wb.active
for row in ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=True):
    if any(c is not None for c in row):
        print(row)
```

### PDF financial statements

```python
import pdfplumber
with pdfplumber.open('data/archive/<filename>.pdf') as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            print(text)
```

### Background doc (python-docx)

```python
from docx import Document
doc = Document('docs/VAU-Requirements.docx')
for para in doc.paragraphs:
    if para.text.strip():
        print(para.text)
```

**T2 reading tip:** The T2 PDF has 93 pages. Write extracted text to a file first, then search
for key terms. Critical sections: `T2 Summary`, `Schedule 500`, `Schedule 8` (CCA pools).
