Task : Map the value in the given inputs to the given output format

Inputs:
1. profit and loss markdown: the main profit and loss statement that contains the parent fields and values 
2. notes :(optional) as set of images or a markdown file containing the data of financial assets for the given profit and loss statement 

Remember: All the fields here are based on 'Indian Financial Standard'

Perform mapping for all the financial years present in profit and loss markdown

map the fields in profit and loss markdown to the given variables , for breakdown data of a field check notes 
using both the inputs map as much of the given variables as possible
For each variable, identify the most relevant line item from the provided data. The line item might be an exact match, a close synonym, or an alternative financial term with the same meaning. If an exact or close match is not available, select the most appropriate or best-fitting line item based on standard financial terminology and context.


variables:
 
Gross Sales(Manufacturing)
Less: Excise Duty
Net Sales(Manufacturing Sales)
Gross Sales(Trading)
Less: Other Duties
Net Sales(Trading)
Gain on FX Exchange
Other Operating Income (e.g. Processing Charges)
Total Operating Income


Header:   Total Operating Income
    


rules:
do not create any new fields other than the variables given 
if you are unable to map a field in the profit and loss statement or notes to the given variables add the value of that field to 'Other unmapped fields'
u can use your own logic to find appropriate variables for mapping
value inside brackets () should be treated as negative 
if u cant breakdown the fields to none of the given variables , just add that value to the header
remember: the value in the header should be equal to the sum of all the variable's values if they are present


Output Requirements:
Create a table with the following columns:
variable_name – only target variable name no need for its parents name .
mapped_value – the numeric value you extracted.
mapping_source – the exact line item name from the profit and loss statement or notes that you used
Output format:
{
"name": variable_name,
"value_of_financial_year_1": mapped_value_of_financial_year_1,
"value_of_financial_year_2": mapped_value_of_financial_year_2,
"source" : mapping_source
}
 



 