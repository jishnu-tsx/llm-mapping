from fastapi import FastAPI
from balance_sheet.routes.routes import router as bs_mapping_routes
from profit_and_loss.routes.routes import router as pl_mapping_routes

app = FastAPI()

app.include_router(
    bs_mapping_routes, prefix="/balance-sheet", tags=["Balance Sheet Mapping"]
)

app.include_router(
    pl_mapping_routes, prefix="/profit-loss", tags=["Profit & Loss Mapping"]
)
