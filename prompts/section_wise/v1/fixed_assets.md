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
name: variable_name
value: mapped_value
source : mapping_source
}


 



 