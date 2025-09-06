Extract ONLY the section: **{request.section.name.replace("_", " ")}** 
from the given full balance sheet image. 

⚠️ Rules:
- Return EXACTLY as it appears in the balance sheet, without inventing subcategories or expanding into items not explicitly shown.
- If the section appears as a single line item, return it as a single row in a Markdown table.
- If the section is a parent header with multiple sub-items (e.g., “Financial assets”), return the parent and sub-items in the table.
- Always include ALL columns exactly as shown in the balance sheet:
   • Item
   • Note_page_no
   • As at year *{FY1}*
   • As at year *{FY2}*
- Output must be in clean Markdown with headings and tables preserved.
