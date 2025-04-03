import shutil
from fastapi import UploadFile
import os

def save_uploaded_file(file: UploadFile, upload_dir: str) -> str:
    """Guarda el archivo subido en el directorio especificado."""
    file_path = os.path.join(upload_dir, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return file_path
    except Exception as e:
        print(f"Error saving file: {e}")
        return None
