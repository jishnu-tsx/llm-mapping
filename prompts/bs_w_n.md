Task: Balance Sheet Field Mapping
You are given a set of balance sheet images and notes images (each image filename corresponds to its page number). Your job is to map the values from these images into the target variables provided.

Rules for Mapping:

Extract data: First, read the fields and values from the balance sheet and notes images.



Identify relevant fields: Match each target variable with the most relevant line item.

If the line item name exactly matches → use it.

If it is a synonym or close equivalent → use it.

If no clear match exists → leave it unmapped and place it under “Other unmapped fields.”

Use notes for breakdowns:

If a variable requires detailed breakdown, check the Notes images corresponding to the balance sheet.

The note page no will be in the main balance sheet in the particular field , use the page no to identify note, some time note no will also be available use that if available

Pick pre-depreciation values: If multiple values exist (before and after depreciation), always take the before depreciation value.

Negative values: Any value inside brackets () should be treated as negative.

No new variables: Only map to the provided variables. Do not invent new fields.

Variables:


ASSETS
CURRENT ASSETS
Inventories
Raw Materials
Stock in process
Finished Goods
Consumable Spares
Trade Debtors
Domestic Debtors over six months
Domestic Debtors less than six months
Export Debtors over six months
Export Debtors less than six months
Other Current Assets
Cash and Bank Balance
Prepaid Expenses
Advance Tax
Deposits with Excise and Sales Tax
Current Assets-Loans and Advances
Sundry Deposits/Earnest Money Deposit (EMD)
Balance with Govt Authorities
Other Advances
Advance to Supplier
Others
FIXED ASSETS
Land & Buildings
Plant & Machinery
Sundries
Less: Depreciation to date
Net Fixed Assets
Capital Work in Progress
NON-CURRENT ASSETS
Investments in/Loans to subsidiaries/
Others Non Current Assets
Investment in other companies
Investment in Mutual Funds
Non-Current Assets-Loans and Advances
Overdue debtors
Deposits with EB,etc.
Non-Moving Inventories
Others
Deferred Tax Asset
INTANGIBLE ASSETS/MISC EXPENDITURE
LIABILITIES
CURRENT LIABILITIES
Working Capital Borrowings
Borrowings from Applicant Bank
From other Banks
Commercial Paper
Creditors for Purchases
Other Current Liabilities
Creditiors for Expenses
Provision for Tax
Long Term Debt due within one year
Outstanding Expenses
Advances From Customer
Others (Curr. Liabilities / Provisions)
Creditors on Capital Account
LONG TERM LIABILITIES
Term Loan from Yes Bank
Term Loan from institutions/Banks
Other Long Term Liabilities
Preference Shares (Repayment Due within 3 years / maturity of our facility)
Fixed Deposits
Foreign currency loans
Debentures
Others (Sales Tax Deferment Loan)
Long term liability to be taken as Quasi Equity
Total Other Long Term Liabilities
CAPITAL AND SURPLUS
Paid up Capital
Preference Share Capital
Reserves and Surplus
Revaluation Reserves
Loss Bought Forward
Deferred Tax Liability
Contingent Liabilities


Output Requirements:

Create a table with the following columns:

variable_name – only the target variable name (no parent name).

mapped_value – the numeric value extracted.

mapping_source – the exact line item name from the balance sheet or notes used.

page_no – the page number where the mapping was found (from the image filename).

Output format:
{
  "name": "variable_name",
  "value": mapped_value,
  "source": "mapping_source",
  "page_no": "page_number"
}