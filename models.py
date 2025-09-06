from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class BalanceSheetSectionEnum(str, Enum):
    # Assets
    INVENTORIES = "Inventories"
    DEBTORS = "Debtors"
    EQUITY = "Equity"
    OTHER_CURRENT_ASSETS = "Other current Assets"
    CURRENT_LIABILITIES = "Current Liabilities"
    FIXED_ASSETS = "Fixed Assets"
    GROSS_FIXED_ASSETS = "Gross Fixed Assets"
    LONG_TERM_LIABILITIES = "Long Term Liabilities"
    NON_CURRENT_ASSETS = "Non-Current Assets"
    WORKING_CAPITAL_BORROWINGS = "Working Capital Borrowings"


class BsCompleteMappingWithNotesRequest(BaseModel):
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
    bs_start_page: int = Field(
        ...,
        description="Starting page number of the Balance Sheet section in the PDF.",
        example=5,
    )
    bs_end_page: int = Field(
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


class BSSectionMappingRequestModel(BaseModel):
    section: BalanceSheetSectionEnum = Field(
        ...,
        description="The section of the balance sheet to extract and map.",
        example="CURRENT_ASSETS",
    )
    company_id: str = Field(
        ...,
        description="Unique identifier of the company.",
        example="COMP12345",
    )
    file_id: str = Field(
        ...,
        description="Unique identifier of the uploaded AFS (Annual Financial Statement) file.",
        example="FILE67890",
    )
    bs_start_page: int = Field(
        ...,
        description="Starting page number of the balance sheet in the PDF.",
        example=5,
    )
    bs_end_page: int = Field(
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
