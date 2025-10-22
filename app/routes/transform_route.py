from fastapi import APIRouter, UploadFile, File
from typing import List
from app.services.transform_service import process_files

router = APIRouter()

# file upload api

@router.post("/transform")
async def transform_jsons(files: List[UploadFile] = File(...)):
    """Upload multiple JSON files → transform → return results."""
    results = process_files(files)
    return {"message": "Transformation completed", "results": results}
