import os
import json
import uuid
import io
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse

app = FastAPI()
UPLOAD_FOLDER = "uploads"

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    file_location = os.path.join(UPLOAD_FOLDER, file.filename)

    try:
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {e}")

    try:
        df = pd.read_csv(file_location)

        response = {
            "filename": file.filename,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "summary": df.describe(include="all").fillna("").to_dict()
        }

        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV: {e}")

@app.get("/files")
def list_uploaded_files():
    try:
        files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".csv")]
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {e}")
    
@app.post("/download-json")
async def download_json(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

        summary = {
            "filename": file.filename,
            "columns": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "summary": json.loads(df.describe(include="all").fillna("").to_json())
        }

        # Crear archivo temporal JSON
        output_filename = f"{uuid.uuid4()}.json"
        output_path = os.path.join("tmp", output_filename)
        os.makedirs("tmp", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=4)

        return FileResponse(path=output_path, filename="report.json", media_type="application/json")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating JSON: {e}")