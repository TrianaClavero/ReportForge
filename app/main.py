from fastapi import FastAPI, UploadFile, File, HTTPException
from io import StringIO
import pandas as pd

app = FastAPI()

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    try:
        contents = await file.read()
        decoded = contents.decode("utf-8")  # <- aquí está el cambio
        df = pd.read_csv(StringIO(decoded))

        preview = df.head().to_dict(orient="records")
        return {
            "columns": df.columns.tolist(),
            "preview": preview,
            "rows": len(df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV: {str(e)}")
