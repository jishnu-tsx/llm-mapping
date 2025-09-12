from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ProfitAndLossSectionEnum(str, Enum):
    # Assets
    REVENUE_FROM_OPERATIONS = "Revenue from Operations"
    OTHER_INCOME = "Other Income"
    COST_OF_GOODS_SOLD = "Cost of Goods Sold"
    EMPLOYEE_BENEFITS_EXPENSES = "Employee Benefits Expense"
    OTHER_OPERATING_AND_ADMINISTRATIVE_EXPENSES = (
        "Other Operating & Administrative Expenses"
    )
    EBITDA = "EBITDA"
    # OPERATING_PROFIT = "Operating Profit (EBIT)"
    FINANCE_COSTS = "Finance Costs"
    PBEIT = "Profit before Exceptional Items & Tax (EBT before exceptional)"
    EXCEPTIONAL_ITEMS = "Exceptional Items"
    # PROFIT_BEFORE_TAX = "Profit before Tax (EBT)"
    TAX_EXPENSES = "Tax Expenses"
    # PROFIT_AFTER_TAX = "Profit after Tax (EAT)"
    APPROPRIATIONS = "Appropriations"
    # NET_CASH_ACCURALS = "(EAT + Depreciation + Amortisation – Dividend)"


class PLCompleteMappingWithNotesRequest(BaseModel):
    company_id: str = Field(
        ...,
        description="Unique identifier of the company.",
        example="COMP12345",
    )
    guid: str = Field(
        ...,
        description="Unique request or processing identifier (used for tracking).",
        example="GUID-ABC-987654",
    )
    file_id: str = Field(
        ...,
        description="Unique identifier of the uploaded AFS (Annual Financial Statement) PDF file.",
        example="FILE67890",
    )
    pl_start_page: int = Field(
        ...,
        description="Starting page number of the Balance Sheet section in the PDF.",
        example=5,
    )
    pl_end_page: int = Field(
        ...,
        description="Ending page number of the Balance Sheet section in the PDF.",
        example=12,
    )
    notes_start_page: Optional[int] = Field(
        None,
        description="Starting page number of the Notes section in the PDF.",
        example=30,
    )
    notes_end_page: Optional[int] = Field(
        None,
        description="Ending page number of the Notes section in the PDF.",
        example=50,
    )


class PLSectionMappingRequestModel(BaseModel):
    section: ProfitAndLossSectionEnum = Field(
        ...,
        description="The section of the balance sheet to extract and map.",
        example="CURRENT_ASSETS",
    )

    company_id: str = Field(
        ...,
        description="Unique identifier of the company.",
        example="COMP12345",
    )
    fy1: str = Field(..., example="2023")
    fy2: str = Field(..., example="2022")
    file_id: str = Field(
        ...,
        description="Unique identifier of the uploaded AFS (Annual Financial Statement) file.",
        example="FILE67890",
    )
    pl_start_page: int = Field(
        ...,
        description="Starting page number of the balance sheet in the PDF.",
        example=5,
    )
    pl_end_page: int = Field(
        ...,
        description="Ending page number of the balance sheet in the PDF.",
        example=12,
    )
    note_page_nos: List[int] = Field(
        ...,
        description="List of page numbers in the PDF where relevant notes for the section are found.",
        example=[30, 31, 32],
    )

    # CURRENT_ASSETS = "Current Assets"
    # INTANGIBLE_ASSETS = "Intangible Assets / Misc Expenditure"
    # TOTAL_ASSETS = "Total Assets"

    # # Liabilities
    # CURRENT_LIABILITIES = "Current Liabilities"
    # CAPITAL_AND_SURPLUS = "Capital and Surplus"
    # TOTAL_LIABILITIES = "Total Liabilities"

    # # Special
    # CONTINGENT_LIABILITIES = "Contingent Liabilities"
