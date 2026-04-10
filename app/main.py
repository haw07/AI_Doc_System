from fastapi import FastAPI
from app.routes import document

app = FastAPI(title="AI Document Intelligence API")

app.include_router(document.router)