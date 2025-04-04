from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
from io import StringIO

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    try:
        contents = await file.read()
        decoded = contents.decode("utf-8")
        df = pd.read_csv(StringIO(decoded))

        response = {
            "filename": file.filename,
            "columns": list(df.columns),
            "dtypes": df.dtypes.apply(str).to_dict(),
            "summary": df.describe(include="all").fillna("").to_dict()
        }

        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")
