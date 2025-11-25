from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pypdf import PdfReader, PdfWriter
import shutil
import os

app = FastAPI()

@app.post("/merge-multiple-files-to-pdf")
async def merge_multiple_files_to_pdf(
    pdf_file: UploadFile = File(...),
    data_files: list[UploadFile] = File(...)
):
    # Validate PDF
    if not pdf_file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a PDF")

    # Validate data files (must be JSON or XML)
    for file in data_files:
        if not (file.filename.lower().endswith(".json") or
                file.filename.lower().endswith(".xml")):
            raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}. Only JSON/XML allowed.")

    # Save uploaded PDF
    pdf_path = f"temp_{pdf_file.filename}"
    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(pdf_file.file, f)

    # Read PDF
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Save and attach all JSON/XML files
    temp_files = []
    for file in data_files:
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        temp_files.append(temp_path)

        with open(temp_path, "rb") as f:
            writer.add_attachment(file.filename, f.read())

    # Write final merged PDF
    output_pdf = f"merged_{pdf_file.filename}"
    with open(output_pdf, "wb") as f:
        writer.write(f)

    # Clean up temp files
    os.remove(pdf_path)
    for temp in temp_files:
        os.remove(temp)

    return FileResponse(output_pdf, media_type="application/pdf", filename=output_pdf)
