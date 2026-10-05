import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, File, UploadFile, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.pipeline import ProcessingPipeline

app = FastAPI(
    title="ZaWolf AI Clinical Extraction API",
    description="Stateless Enterprise AI Microservice for Medical Document Extraction",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = ProcessingPipeline(ocr_engine="auto")

class HealthResponse(BaseModel):
    status: str
    ocr_engine_default: str
    llm_model: str

@app.get("/", tags=["General"])
def root():
    return {
        "system": "ZaWolf AI Clinical Extraction Microservice",
        "version": "2.1.0",
        "developer": "Eng. Saad Tamer",
        "status": "Stateless API Mode"
    }

@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "ocr_engine_default": pipeline.ocr_engine,
        "llm_model": pipeline.llm_processor.llm.model
    }

@app.post("/api/v1/process", tags=["Pipeline"])
async def process_document(
    file: UploadFile = File(...),
    ocr_engine: str = Query("auto", description="OCR Engine: 'auto', 'paddle', or 'qwen'")
):
    """
    STATELESS ENDPOINT:
    Ingests a document, extracts structured JSON, and returns it WITHOUT saving to any local database.
    Perfect for microservice integration with external EHRs like CareOS.
    """
    if ocr_engine not in ["auto", "paddle", "qwen"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ocr_engine must be 'auto', 'paddle', or 'qwen'"
        )

    pipeline.ocr_engine = ocr_engine
    
    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_path = Path(temp_file.name)
        shutil.copyfileobj(file.file, temp_file)

    start_time = time.perf_counter()
    try:
        result = pipeline.process_file(temp_path)
        elapsed = time.perf_counter() - start_time

        return {
            "file_name": file.filename,
            "status": "success",
            "processing_time_seconds": round(elapsed, 2),
            "extracted_data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(e)}"
        )
    finally:
        if temp_path.exists():
            try:
                os.remove(temp_path)
            except Exception:
                pass
