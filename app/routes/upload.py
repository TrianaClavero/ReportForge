from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_handler import save_uploaded_file
import os

router = APIRouter()

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True) 

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_path = save_uploaded_file(file, UPLOAD_DIR)
    if file_path:
        return {"filename": file.filename, "message": "File uploaded successfully"}
    raise HTTPException(status_code=500, detail="File upload failed")
