from fastapi import FastAPI
from routes import router as mapping_routes

app = FastAPI()

app.include_router(mapping_routes)
