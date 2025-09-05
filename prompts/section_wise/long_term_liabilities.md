Task : Map the value in the given inputs to the given output format

Inputs:
1. balance_sheet.md : the main balansheet that contains the parent fields and values 
2. notes :(optional) a markdown file containing the data of financial assets for a balance sheet 

Remember: All the fields here are based on 'Indian Financial Standard'

Perform mapping for all the financial years present in balance_sheet.md 

map the fields in balance_sheet.md to the given variables , for breakdown data of a field check notes 
using both the markdowns map as much of the given variables as possible
For each variable, identify the most relevant line item from the provided data. The line item might be an exact match, a close synonym, or an alternative financial term with the same meaning. If an exact or close match is not available, select the most appropriate or best-fitting line item based on standard financial terminology and context.



 
 Preference Shares (Repayment Due within 3 years / maturity of our facility) 
 Fixed Deposits 
 Foreign currency loans 
 Debentures 
 Others (Sales Tax Deferment Loan) 
 Long term liability to be taken as Quasi Equity  
 Total Other Long Term Liabilities 


Header:  LONG TERM LIABILITIES 
    


rules:
do not create any new fields other than the variables given 
if you are unable to map a field in the balance sheet or notes to the given variables add the value of that field to 'Other unmapped fields'
u can use your own logic to find appropriate variables for mapping
value inside brackets () should be treated as negative 
if u cant breakdown the fields to none of the given variables , just add that value to the header
remember: the value in the header should be equal to the sum of all the variable's values if they are present


Output requirements:


a table containing the variables and the value mapped to it along with from which markdown which field these values are exracted 




give the output in the same order 
do not create any fields in other than the given variables