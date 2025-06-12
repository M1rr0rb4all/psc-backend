from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from psc_utils import get_ownership_tree
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/tree")
def get_tree(company_name: str):
    api_key = os.getenv("CH_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not set")
    try:
        data = get_ownership_tree(company_name, api_key)
        return {"tree": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
