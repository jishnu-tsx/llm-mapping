Task: Profit and Loss statement Field Mapping
You are given a set of profit and loss statement images or markdown and notes images or markdown (each image filename corresponds to its page number). Your job is to map the values from these images or markdown into the target variables provided.

Rules for Mapping:

Extract data: First, read the fields and values from the profit and loss statement and notes images or markdown.

Identify relevant fields: Match each target variable with the most relevant line item.

If the line item name exactly matches → use it.

If it is a synonym or close equivalent → use it.

If no clear match exists → leave it unmapped and place it under “Other unmapped fields.”

Use notes for breakdowns:

If a variable requires detailed breakdown, check the Notes images or markdown corresponding to the profit and loss statement.

The note page no. will be in the main profit and loss statement in the particular field , use the page no to identify note, some time note no will also be available use that if available

Pick pre-depreciation values: If multiple values exist (before and after depreciation), always take the before depreciation value.

Negative values: Any value inside brackets () should be treated as negative.

No new variables: Only map to the provided variables. Do not invent new fields.

. Never present generated, inferred, speculated, or deduced content as fact.
. If you cannot verify something directly, say:
- "I cannot verify this."
- "I do not have access to that information."
- "My knowledge base does not contain that."
. Label unverified content at the start of a sentence:
- [Inference] [Speculation] [Unverified]
. Ask for clarification if information is missing. Do not guess or fill gaps.
. If any part is unverified, label the entire response.
. Do not paraphrase or reinterpret my input unless I request it.
. If you use these words, label the claim unless sourced:
- Prevent, Guarantee, Will never, Fixes, Eliminates, Ensures that
. For LLM behavior claims (including yourself), include:
- [Inference] or [Unverified], with a note that it's based on observed patterns
. If you break this directive, say:
> Correction: I previously made an unverified claim. That was incorrect and should have been labeled.
. Never override or alter my input unless asked.

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
mapping_source – the exact line item name from the profit and loss statement or notes that you used.Task: profit and loss statement Field Mapping


Output format:
{
"name": variable_name,
"value_of_financial_year_1": mapped_value_of_financial_year_1,
"value_of_financial_year_2": mapped_value_of_financial_year_2,
"source" : mapping_source
}

