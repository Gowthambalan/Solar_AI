# from fastapi import APIRouter, UploadFile, File
# from typing import List
# from app.services.transform_service import process_files

# router = APIRouter()

# @router.post("/transform")
# async def transform_jsons(files: List[UploadFile] = File(...)):
#     """Upload multiple JSON files → transform → return results."""
#     results = process_files(files)
#     return {"message": "Transformation completed", "results": results}


from fastapi import APIRouter, UploadFile, File
from typing import List
from app.config.constants import CLEANED_DIR, OUTPUT_DIR
from app.services.transform_service import process_files
from app.utils.anamoly_dedection import process_bulk_json_folder
from app.utils.mongo_utils import initialize_mongo_connection, insert_bulk_json_folder

router = APIRouter()

# file upload api

@router.post("/transform")
async def transform_jsons(files: List[UploadFile] = File(...)):
    """Upload multiple JSON files → transform → return results."""
    results = process_files(files)


    process_bulk_json_folder(OUTPUT_DIR, CLEANED_DIR)
    initialize_mongo_connection()
    insert_bulk_json_folder(CLEANED_DIR)
    return {"message": "Transformation completed", "results": results}
 