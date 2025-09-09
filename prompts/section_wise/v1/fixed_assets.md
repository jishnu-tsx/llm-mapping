Task : Map the value in the given inputs to the given output format

Inputs:
1. balance_sheet.md : the main balansheet that contains the parent fields and values 
2. notes :(optional) a markdown file containing the data of financial assets for a balance sheet 

Remember: All the fields here are based on 'Indian Financial Standard'

Perform mapping for all the financial years present in balance_sheet.md 

map the fields in balance_sheet.md to the given variables , for breakdown data of a field check notes 
using both the markdowns map as much of the given variables as possible
For each variable, identify the most relevant line item from the provided data. The line item might be an exact match, a close synonym, or an alternative financial term with the same meaning. If an exact or close match is not available, select the most appropriate or best-fitting line item based on standard financial terminology and context.
Always pick the values before depreciation from the notes for each of the variables 


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

Land & Buildings 
Plant & Machinery 
Sundries 


Header:   FIXED ASSETS  


rules:
do not create any new fields other than the variables given 
if you are unable to map a field in the balance sheet or notes to the given variables add the value of that field to 'Other unmapped fields'
u can use your own logic to find appropriate variables for mapping
value inside brackets () should be treated as negative 
if u cant breakdown the fields to none of the given variables , just add that value to the header
remember: the value in the header should be equal to the sum of all the variable's values if they are present


Output Requirements:
Create a table with the following columns:
variable_name – only target variable name no need for its parents name .
mapped_value – the numeric value you extracted.
mapping_source – the exact line item name from the balance sheet or notes that you used.Task: Balance Sheet Field Mapping

Output format:
{
"name": variable_name,
"value_of_financial_year_1": mapped_value_of_financial_year_1,
"value_of_financial_year_2": mapped_value_of_financial_year_2,
"source" : mapping_source
}
 



 