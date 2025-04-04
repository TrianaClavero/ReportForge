import os
import json
import uuid
import io
import pdfkit
import pandas as pd
from fastapi import (
    FastAPI, 
    UploadFile, 
    File,
    HTTPException, 
    Request)
from fastapi.responses import (
    FileResponse,
    JSONResponse,
    HTMLResponse,
    Response
)
from fastapi.templating import Jinja2Templates

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

        output_filename = f"{uuid.uuid4()}.json"
        output_path = os.path.join("tmp", output_filename)
        os.makedirs("tmp", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=4)

        return FileResponse(path=output_path, filename="report.json", media_type="application/json")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating JSON: {e}")

templates = Jinja2Templates(directory="app/templates")

@app.post("/report", response_class=HTMLResponse)
async def generate_report(request: Request, file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

        summary = df.describe(include="all").to_dict()
        summary = {k: {stat: ("" if pd.isna(v) else v) for stat, v in v_dict.items()} for k, v_dict in summary.items()}

        return templates.TemplateResponse("report.html", {
            "request": request,
            "filename": file.filename,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.apply(str).to_dict(),
            "summary": summary,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
    
@app.post("/report/pdf")
async def generate_report_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {str(e)}")

    summary = df.describe(include='all').to_dict()
    dtypes = df.dtypes.astype(str).to_dict()
    columns = df.columns.tolist()

    html = templates.get_template("report.html").render(
        filename=file.filename,
        columns=columns,
        dtypes=dtypes,
        summary=summary,
    )

    try:
        pdf = pdfkit.from_string(html, False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

    return Response(content=pdf, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename={file.filename.replace('.csv', '')}_report.pdf"
    })    