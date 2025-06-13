from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from psc_utils import build_structure
import os

app = FastAPI()

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("COMPANIES_HOUSE_API_KEY")

@app.get("/ownership-structure/")
async def get_structure(company_name: str):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured")

    try:
        structure = build_structure(company_name, API_KEY)
        return structure
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
