import os
import sys

# Reconfigure stdout/stderr to use UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from api.health import router as health_router
from api.company import router as company_router
from api.dashboard import router as dashboard_router
from api.review import router as review_router
from api.email import router as email_router

load_dotenv()

app = FastAPI(title="Sales Automation API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing/development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(company_router)
app.include_router(dashboard_router)
app.include_router(review_router)
app.include_router(email_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Sales Automation API"}
