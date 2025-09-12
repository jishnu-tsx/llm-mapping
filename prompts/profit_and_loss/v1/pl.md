Task: Profit and loss Field Mapping
You are given a set of Profit and loss statement images or a markdown of the Profit and loss (these contain financial data). Your job is to map the values from these Profit and loss statement into the target variables provided.

Remember: All the fields here are based on 'Indian Financial Standard'

Rules for Mapping:
Extract data: First, read the fields and values from the Profit and loss.
Identify relevant fields: Match each target variable with the most relevant line item in the Profit and loss.
If the line item name exactly matches → use it.
If it is a synonym or a close equivalent → use it.
If no clear match exists → leave it unmapped and place it under “Other unmapped fields.”
Negative values: Any value inside brackets () should be treated as negative.
No new variables: Only map to the provided variables. Do not invent new fields.

Variables:


Gain on sale of Fixed Assets / Investments
Other Income(Excluding Interest Income)
Total Income
Purchases(Finsihed Goods)
Raw Material Consumed
Power Costs(if related to manufacturing)
Logistics Costs
Any other Direct Costs (e.g. Other Manufacturing Expenses)
Increase/(Decrease) in Inventory(Finshed Goods/WIP)
Cost of Goods Sold
Gross Profit(Excluding Depn/other Income)
Employees Employments(To the extent not included in direct costs)
Operational lease payments
Other Costs
Rent
Repair & Maintenance
Loss on Foreign Exchange
Selling/Marketing/Commission/Advertisement Cost
Discount Given
Legal Costs
Insurance
Bad-Debt/Write-off
Operational provisions(Pls Specify)
Total Adminstration Expenses
Total Operating Expenses
EBITDA
Depreciation
Amortization
Total D/A
EBIT
Interest Income recd.
Interest paid
Interest expenses net
EBT before exceptionals
Exceptional income - Cash
Exceptional expenses-Non Cash
Exceptional Income-Non Cash
Exceptional expenses-Cash
EBT
Current Tax
Deferred Tax
EAT
Dividends
Retained Profit
Net Cash Accruals

Output Requirements:
Create a table with the following columns:
variable_name – only target variable name no need for its parents name .
mapped_value – the numeric value you extracted.
mapping_source – the exact line item name from the Profit and loss statement that you used

Output format:
{
"name": variable_name,
"value_of_financial_year_1": mapped_value_of_financial_year_1,
"value_of_financial_year_2": mapped_value_of_financial_year_2,
"source" : mapping_source
}

