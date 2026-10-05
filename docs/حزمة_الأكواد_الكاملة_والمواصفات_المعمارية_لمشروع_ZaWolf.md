# 📦 حزمة الأكواد الكاملة والمواصفات المعمارية الشاملة لمنظومة ZaWolf
## Complete Production Codebase & Architectural Master Bundle (v1.0.0 Final Release)
> **توجيه للنماذج والمطورين:** تحتوي هذه الوثيقة على الكود المصدري الحرفي والكامل لكافة ملفات المشروع دون أي استثناء، إلى جانب الركائز المعمارية ومخططات قاعدة البيانات.

```yaml
project_name: ZaWolf_project
engineer: Eng. Saad Tamer (Data & AI Engineer)
release: v1.0.0 Production Final Release
date: October 2026
total_bundled_files: 39
evaluation_benchmark: 100% PASS across all 8 input files
persistence: Atomic single transaction commit/rollback across 19 SQL Server tables
```

---

## فهرس الملفات البرمجية المضمنة بالكامل:

1. [`config\settings.py`](#file-config-settings-py)
2. [`src\api.py`](#file-src-api-py)
3. [`run_api.py`](#file-run_api-py)
4. [`evaluate_input_files.py`](#file-evaluate_input_files-py)
5. [`main.py`](#file-main-py)
6. [`src\pipeline.py`](#file-src-pipeline-py)
7. [`src\utils.py`](#file-src-utils-py)
8. [`src\ingestion\file_detector.py`](#file-src-ingestion-file_detector-py)
9. [`src\ingestion\router.py`](#file-src-ingestion-router-py)
10. [`src\processors\pdf_processor.py`](#file-src-processors-pdf_processor-py)
11. [`src\processors\word_processor.py`](#file-src-processors-word_processor-py)
12. [`src\processors\structured_processor.py`](#file-src-processors-structured_processor-py)
13. [`src\processors\image_processor.py`](#file-src-processors-image_processor-py)
14. [`src\processors\extraction_schema.py`](#file-src-processors-extraction_schema-py)
15. [`src\ocr\device.py`](#file-src-ocr-device-py)
16. [`src\ocr\ocr_engine.py`](#file-src-ocr-ocr_engine-py)
17. [`src\ocr\handwriting_ocr.py`](#file-src-ocr-handwriting_ocr-py)
18. [`src\ocr\ocr_router.py`](#file-src-ocr-ocr_router-py)
19. [`src\ocr\ocr_utils.py`](#file-src-ocr-ocr_utils-py)
20. [`src\llm\local_llm.py`](#file-src-llm-local_llm-py)
21. [`src\llm\llm_processor.py`](#file-src-llm-llm_processor-py)
22. [`src\llm\llm_schema.py`](#file-src-llm-llm_schema-py)
23. [`src\validation\extraction_guard.py`](#file-src-validation-extraction_guard-py)
24. [`src\validation\validator.py`](#file-src-validation-validator-py)
25. [`src\database\database.py`](#file-src-database-database-py)
26. [`src\database\mapper.py`](#file-src-database-mapper-py)
27. [`src\database\relation_resolver.py`](#file-src-database-relation_resolver-py)
28. [`src\database\repository.py`](#file-src-database-repository-py)
29. [`src\database\client_repository.py`](#file-src-database-client_repository-py)
30. [`src\database\appointment_repository.py`](#file-src-database-appointment_repository-py)
31. [`src\database\consent_repository.py`](#file-src-database-consent_repository-py)
32. [`src\database\invoice_repository.py`](#file-src-database-invoice_repository-py)
33. [`src\database\invoice_item_repository.py`](#file-src-database-invoice_item_repository-py)
34. [`src\database\package_repository.py`](#file-src-database-package_repository-py)
35. [`src\database\client_package_repository.py`](#file-src-database-client_package_repository-py)
36. [`src\database\payment_repository.py`](#file-src-database-payment_repository-py)
37. [`src\database\photo_repository.py`](#file-src-database-photo_repository-py)
38. [`src\database\source_document_repository.py`](#file-src-database-source_document_repository-py)
39. [`src\database\treatment_repository.py`](#file-src-database-treatment_repository-py)

---

## الكود المصدري الحرفي لكافة ملفات المشروع (Verbatim Source Code):

<a id='file-config-settings-py'></a>
### الملف: `config\settings.py`
**المسار الكامل:** `E:\ZaWolf_project\config\settings.py`

```python
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = DATA_DIR / "output"
IMAGE_PROCESSED_DIR = PROCESSED_DIR / "images"
PDF_IMAGES_DIR = PROCESSED_DIR / "pdf_images"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"


MAX_BATCH_TEXT_SIZE = 12000

BATCH_MEMORY_SAFETY_RATIO = 0.25


SUPPORTED_IMAGE_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
]


SUPPORTED_EXTENSIONS = {
    ".pdf": "pdf",
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
    ".webp": "image",
    ".xlsx": "excel",
    ".xls": "excel",
    ".csv": "csv",
    ".docx": "word",
}
```

<a id='file-src-api-py'></a>
### الملف: `src\api.py`
**المسار الكامل:** `E:\ZaWolf_project\src\api.py`

```python
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, File, UploadFile, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pyodbc

from src.pipeline import ProcessingPipeline
from src.database.database import Database

app = FastAPI(
    title="ZaWolf Medical Document Processing API",
    description="Enterprise On-Premise Clinical Document Extraction, Multimodal Vision OCR & SQL Server Persistence API",
    version="2.0.0"
)

# Enable CORS for frontend/mobile apps (React, Flutter, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = ProcessingPipeline(ocr_engine="auto")
db = Database()


class HealthResponse(BaseModel):
    status: str
    database_connected: bool
    database_name: str
    ocr_engine_default: str
    llm_model: str


class ProcessResponse(BaseModel):
    file_name: str
    status: str
    processing_time_seconds: float
    inserted_ids: Dict[str, Any]
    errors: List[Any]
    extracted_data: Optional[Dict[str, Any]] = None


@app.get("/", tags=["General"])
def root():
    return {
        "system": "ZaWolf Medical Document Processing Pipeline",
        "version": "2.0.0",
        "developer": "Eng. Saad Tamer",
        "documentation": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    db_ok = False
    db_name = "Unavailable"
    try:
        db_name = db.test_connection()
        db_ok = True
    except Exception as e:
        db_name = f"Error: {e}"

    return {
        "status": "healthy" if db_ok else "degraded",
        "database_connected": db_ok,
        "database_name": db_name,
        "ocr_engine_default": pipeline.ocr_engine,
        "llm_model": pipeline.llm_processor.llm.model
    }


@app.post("/api/v1/process", response_model=ProcessResponse, tags=["Pipeline"])
async def process_document(
    file: UploadFile = File(...),
    ocr_engine: str = Query("auto", description="OCR Engine: 'auto', 'paddle', or 'qwen'")
):
    """
    Ingests and processes any medical document (Digital PDF, Scanned PDF, Word, Excel, CSV, or Image),
    extracts structured clinical entities via local LLM / OCR, and atomically persists data to SQL Server.
    """
    if ocr_engine not in ["auto", "paddle", "qwen"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ocr_engine must be 'auto', 'paddle', or 'qwen'"
        )

    pipeline.ocr_engine = ocr_engine
    
    # Save uploaded file to a temporary location
    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_path = Path(temp_file.name)
        shutil.copyfileobj(file.file, temp_file)

    start_time = time.perf_counter()
    try:
        result = pipeline.process_and_save_file(temp_path)
        elapsed = time.perf_counter() - start_time

        return {
            "file_name": file.filename,
            "status": result.get("status", "unknown"),
            "processing_time_seconds": round(elapsed, 2),
            "inserted_ids": result.get("inserted", {}),
            "errors": result.get("errors", []),
            "extracted_data": result.get("data")
        }
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(e)}"
        )
    finally:
        # Cleanup temporary file
        if temp_path.exists():
            try:
                os.remove(temp_path)
            except Exception:
                pass


@app.get("/api/v1/documents", tags=["Audit & Documents"])
def list_recent_documents(limit: int = Query(20, ge=1, le=100)):
    """Fetches recently processed documents from the source_documents audit table."""
    try:
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT TOP {limit} id, file_name, doc_type, review_status, created_at 
            FROM source_documents 
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()
        docs = []
        for r in rows:
            docs.append({
                "id": r[0],
                "file_name": r[1],
                "doc_type": r[2],
                "review_status": r[3],
                "created_at": str(r[4])
            })
        return {"total": len(docs), "documents": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            conn.close()
        except Exception:
            pass


@app.get("/api/v1/metrics", tags=["Metrics & Statistics"])
def get_system_metrics():
    """Returns real-time database record counts across core medical tables."""
    tables = ["clients", "medications", "vitals", "medical_history", "locations", "services", "source_documents"]
    counts = {}
    try:
        conn = db.connect()
        cursor = conn.cursor()
        for t in tables:
            cursor.execute(f"SELECT COUNT(*) FROM [{t}]")
            counts[t] = cursor.fetchone()[0]
        return {"database": "ZaWolfDB", "table_counts": counts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            conn.close()
        except Exception:
            pass

```

<a id='file-run_api-py'></a>
### الملف: `run_api.py`
**المسار الكامل:** `E:\ZaWolf_project\run_api.py`

```python
import uvicorn

if __name__ == "__main__":
    print("================================================================================")
    print("🐺 STARTING ZAWOLF MEDICAL PROCESSING REST API GATEWAY")
    print("================================================================================")
    print("Server running on: http://localhost:8000")
    print("Interactive Swagger UI Docs: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/api/v1/health")
    print("================================================================================\n")
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=False)

```

<a id='file-evaluate_input_files-py'></a>
### الملف: `evaluate_input_files.py`
**المسار الكامل:** `E:\ZaWolf_project\evaluate_input_files.py`

```python
import os
import sys
import time
from pathlib import Path

# Force UTF-8 encoding for clean terminal output in Windows
sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline import ProcessingPipeline

INPUT_DIR = PROJECT_ROOT / "data" / "input"


def format_inserted(inserted_dict):
    """Summarizes non-empty inserted IDs."""
    if not isinstance(inserted_dict, dict):
        return "None"
    items = [f"{table}: {len(ids)}" for table, ids in inserted_dict.items() if ids]
    return ", ".join(items) if items else "Audit Only (source_documents)"


def main():
    print("=" * 85)
    print("🐺 ZAWOLF INPUT DATASET EVALUATION & BENCHMARK SUITE")
    print(f"📁 Target Directory: {INPUT_DIR}")
    print("=" * 85)

    if not INPUT_DIR.exists():
        print(f"❌ Error: Directory not found: {INPUT_DIR}")
        return

    # Collect all supported files
    supported_extensions = {".pdf", ".docx", ".csv", ".xlsx", ".png", ".jpg", ".jpeg"}
    files = [
        p for p in sorted(INPUT_DIR.iterdir())
        if p.is_file() and p.suffix.lower() in supported_extensions
    ]

    total_files = len(files)
    print(f"Found {total_files} files ready for evaluation.\n")

    # Initialize pipeline with auto-adaptive OCR routing and physical core thread detection
    pipeline = ProcessingPipeline(ocr_engine="auto")

    eval_results = []

    for index, file_path in enumerate(files, start=1):
        print("-" * 85, flush=True)
        print(f"[{index}/{total_files}] Processing: {file_path.name}", flush=True)
        print(f"     Type: {file_path.suffix.upper()} | Size: {file_path.stat().st_size / 1024:.1f} KB", flush=True)

        start_time = time.perf_counter()
        try:
            result = pipeline.process_and_save_file(file_path)
            elapsed = time.perf_counter() - start_time

            status = result.get("status", "unknown")
            inserted = result.get("inserted", {})
            errors = result.get("errors", [])
            data = result.get("data") or {}

            # Evaluation verdict
            is_success = status in ["saved", "valid"]
            verdict = "PASS ✅" if is_success else "FAIL ❌"

            # Count extracted entities
            entity_summary = []
            for key, val in data.items():
                if isinstance(val, list) and val:
                    entity_summary.append(f"{key}: {len(val)}")

            print(f"     Result  : {verdict} (Status: {status})", flush=True)
            print(f"     Latency : {elapsed:.2f} seconds", flush=True)
            print(f"     Database: {format_inserted(inserted)}", flush=True)
            if entity_summary:
                print(f"     Entities: {', '.join(entity_summary)}", flush=True)
            if errors:
                print(f"     Errors  : {errors}", flush=True)

            eval_results.append({
                "file": file_path.name,
                "type": file_path.suffix.lower(),
                "status": status,
                "verdict": verdict,
                "elapsed": elapsed,
                "inserted_count": sum(len(ids) for ids in inserted.values() if isinstance(ids, list)),
                "has_errors": bool(errors)
            })

        except Exception as e:
            elapsed = time.perf_counter() - start_time
            print(f"     Result  : FAIL ❌ (Exception: {str(e)})")
            print(f"     Latency : {elapsed:.2f} seconds")
            eval_results.append({
                "file": file_path.name,
                "type": file_path.suffix.lower(),
                "status": "exception",
                "verdict": "FAIL ❌",
                "elapsed": elapsed,
                "inserted_count": 0,
                "has_errors": True
            })

    # Print Final Evaluation Dashboard
    print("\n" + "=" * 85, flush=True)
    print("📊 FINAL EVALUATION & PERFORMANCE DASHBOARD", flush=True)
    print("=" * 85, flush=True)
    print(f"{'#':<3} | {'File Name':<35} | {'Verdict':<8} | {'Status':<7} | {'Time (s)':<8}", flush=True)
    print("-" * 85, flush=True)

    passed_count = 0
    total_time = 0.0

    for idx, r in enumerate(eval_results, start=1):
        file_display = r['file'][:33] + ".." if len(r['file']) > 35 else r['file']
        print(f"{idx:<3} | {file_display:<35} | {r['verdict']:<8} | {r['status']:<7} | {r['elapsed']:<8.2f}", flush=True)
        if "PASS" in r['verdict']:
            passed_count += 1
        total_time += r['elapsed']

    print("=" * 85, flush=True)
    print(f"Total Evaluated: {total_files} files", flush=True)
    print(f"Passed         : {passed_count} / {total_files} ({passed_count / total_files * 100:.1f}%)", flush=True)
    print(f"Failed         : {total_files - passed_count}", flush=True)
    print(f"Total Time     : {total_time:.2f} seconds", flush=True)
    if total_files > 0:
        print(f"Average Time   : {total_time / total_files:.2f} s/file", flush=True)
    print("=" * 85, flush=True)

    # Save to CSV for reporting
    try:
        import pandas as pd
        out_csv = PROJECT_ROOT / "data" / "output" / "evaluation_input_results.csv"
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(eval_results).to_csv(out_csv, index=False, encoding="utf-8-sig")
        print(f"💾 Results saved to: {out_csv}", flush=True)
    except Exception as save_err:
        print(f"⚠️ Warning: Could not save CSV report: {save_err}", flush=True)


if __name__ == "__main__":
    main()

```

<a id='file-main-py'></a>
### الملف: `main.py`
**المسار الكامل:** `E:\ZaWolf_project\main.py`

```python
from src.pipeline import run_pipeline


if __name__ == "__main__":
    results = run_pipeline()

    print("\n" + "=" * 80)
    print("PIPELINE RESULTS")
    print("=" * 80)

    for index, result in enumerate(results, start=1):
        file_info = result.get("file", {})

        print(
            f"{index}. "
            f"{file_info.get('name')} | "
            f"{file_info.get('type')} | "
            f"{result.get('content_type')}"
        )

    print("\n" + "=" * 80)
    print(f"Pipeline completed: {len(results)} files processed.")
    print("=" * 80)
```

<a id='file-src-pipeline-py'></a>
### الملف: `src\pipeline.py`
**المسار الكامل:** `E:\ZaWolf_project\src\pipeline.py`

```python
from pathlib import Path
import json

import pandas as pd

from src.ingestion.file_detector import detect_file_type
from src.ingestion.router import route_file

from src.processors.pdf_processor import (
    detect_pdf_type,
    process_pdf_to_chunks,
    convert_pdf_to_images,
)

from src.processors.word_processor import process_word
from src.processors.structured_processor import extract_structured_data
from src.processors.image_processor import process_image

from src.ocr.ocr_router import OCRRouter

from src.llm.llm_processor import LLMProcessor
from src.validation.validator import DataValidator
from src.database.mapper import DatabaseMapper

from config.settings import PROCESSED_DIR


class ProcessingPipeline:

    def __init__(self, ocr_engine="auto"):
        self.llm_processor = LLMProcessor()
        self.validator = DataValidator()
        self.database_mapper = DatabaseMapper()

        self.ocr_router = OCRRouter()
        self.ocr_engine = ocr_engine

    def process_file(self, file_path):

        try:
            file_info = detect_file_type(file_path)

            if not file_info["supported"]:
                return {
                    "status": "unsupported",
                    "data": None,
                    "source_text": "",
                    "ocr_text": "",
                    "source_metadata": {},
                    "errors": [
                        {
                            "type": "unsupported_file",
                            "message": (
                                f"Unsupported file type: "
                                f"{file_info.get('extension')}"
                            ),
                        }
                    ],
                }

            route = route_file(file_info)

            if route == "pdf_pipeline":
                return self._process_pdf_file(file_info)

            if route in [
                "excel_pipeline",
                "csv_pipeline",
            ]:
                return self._process_structured_file(
                    file_info
                )

            if route == "word_pipeline":
                return self._process_word_file(
                    file_info
                )

            text = self._extract_text(
                file_info,
                route,
            )

            if not text.strip():
                return {
                    "status": "invalid",
                    "data": None,
                    "source_text": "",
                    "ocr_text": "",
                    "source_metadata": {},
                    "errors": [
                        {
                            "type": "empty_text",
                            "message": (
                                "No text extracted from file."
                            ),
                        }
                    ],
                }

            result = self.process_text(text)

            if result["status"] == "valid":
                result["source_text"] = text

                if route == "image_pipeline":
                    result["ocr_text"] = text
                else:
                    result["ocr_text"] = ""

                result["source_metadata"] = {
                    "file_name": Path(
                        file_info["file_path"]
                    ).name,
                    "route": route,
                    "ocr_engine": (
                        self.ocr_engine
                        if route == "image_pipeline"
                        else None
                    ),
                }

            return result

        except Exception as error:

            return {
                "status": "error",
                "data": None,
                "source_text": "",
                "ocr_text": "",
                "source_metadata": {},
                "errors": [
                    {
                        "type": "pipeline_error",
                        "message": str(error),
                    }
                ],
            }

        finally:
            if hasattr(self, "llm_processor") and self.llm_processor:
                try:
                    self.llm_processor.close()
                except Exception:
                    pass

    def process_and_save_file(self, file_path):

        result = self.process_file(
            file_path
        )

        if result["status"] != "valid":
            return result

        if result.get("structured_data") is not None:

            return {
                "status": "valid",
                "data": result.get("data"),
                "structured_data": result.get(
                    "structured_data"
                ),
                "structured_summary": result.get(
                    "structured_summary"
                ),
                "inserted": {},
                "errors": [],
            }

        try:

            data = result["data"]

            source_metadata = result.get(
                "source_metadata",
                {},
            )

            source_text = result.get(
                "source_text",
                "",
            )

            ocr_text = result.get(
                "ocr_text",
                "",
            )

            source_document = (
                self._build_source_document(
                    file_path=file_path,
                    data=data,
                    source_metadata=source_metadata,
                    source_text=source_text,
                    ocr_text=ocr_text,
                )
            )

            if source_document:

                data = data.copy()

                source_documents = list(
                    data.get(
                        "source_documents",
                        [],
                    )
                )

                source_documents.append(
                    source_document
                )

                data["source_documents"] = (
                    source_documents
                )

            inserted = self.database_mapper.save(
                data
            )

            return {
                "status": "saved",
                "data": data,
                "inserted": inserted,
                "errors": [],
            }

        except Exception as error:

            return {
                "status": "error",
                "data": result.get("data"),
                "inserted": {},
                "errors": [
                    {
                        "type": "database_error",
                        "message": str(error),
                    }
                ],
            }

    def process_text(self, text):

        try:

            llm_data = self.llm_processor.process(
                text
            )

            validation_result = (
                self.validator.validate(
                    llm_data
                )
            )

            if not validation_result["valid"]:

                return {
                    "status": "invalid",
                    "data": validation_result.get(
                        "data"
                    ),
                    "source_text": text,
                    "ocr_text": "",
                    "source_metadata": {},
                    "errors": (
                        validation_result.get(
                            "errors",
                            [],
                        )
                    ),
                }

            return {
                "status": "valid",
                "data": validation_result["data"],
                "source_text": text,
                "ocr_text": "",
                "source_metadata": {},
                "errors": [],
            }

        except Exception as error:

            return {
                "status": "error",
                "data": None,
                "source_text": text,
                "ocr_text": "",
                "source_metadata": {},
                "errors": [
                    {
                        "type": "text_processing_error",
                        "message": str(error),
                    }
                ],
            }

    def process_and_save(self, text):

        result = self.process_text(
            text
        )

        if result["status"] != "valid":
            return result

        try:

            data = result["data"]

            inserted = self.database_mapper.save(
                data
            )

            return {
                "status": "saved",
                "data": data,
                "inserted": inserted,
                "errors": [],
            }

        except Exception as error:

            return {
                "status": "error",
                "data": result["data"],
                "inserted": {},
                "errors": [
                    {
                        "type": "database_error",
                        "message": str(error),
                    }
                ],
            }

    def _extract_text(
        self,
        file_info,
        route,
    ):

        file_path = Path(
            file_info["file_path"]
        )

        if route == "word_pipeline":
            return self._process_word(
                file_path
            )

        if route in [
            "excel_pipeline",
            "csv_pipeline",
        ]:
            raise ValueError(
                "Structured files must be processed "
                "through _process_structured_file()."
            )

        if route == "image_pipeline":
            return self._process_image(
                file_path
            )

        raise ValueError(
            f"Unsupported route: {route}"
        )

    def _process_word(
        self,
        file_path,
    ):

        result = process_word(
            file_path
        )

        text_parts = []

        for batch in result:

            if not isinstance(
                batch,
                list,
            ):
                continue

            for chunk in batch:

                if not isinstance(
                    chunk,
                    dict,
                ):
                    continue

                text = chunk.get(
                    "text"
                )

                if text:
                    text_parts.append(
                        text
                    )

        return "\n\n".join(
            text_parts
        )

    def _process_word_file(
        self,
        file_info,
    ):
        file_path = Path(
            file_info["file_path"]
        )

        merged_data = (
            self._create_empty_data()
        )

        batch_count = 0
        text_parts = []

        for batch in process_word(file_path):
            batch_text = "\n\n".join(
                chunk["text"]
                for chunk in batch
                if isinstance(chunk, dict) and chunk.get("text")
            )

            if not batch_text.strip():
                continue

            batch_count += 1
            print(f"       ↳ Processing Word batch {batch_count}...", flush=True)
            text_parts.append(batch_text)

            batch_result = self.process_text(
                batch_text
            )

            if batch_result["status"] != "valid":
                return {
                    "status": batch_result["status"],
                    "data": None,
                    "source_text": "\n\n".join(text_parts),
                    "ocr_text": "",
                    "source_metadata": {},
                    "errors": [
                        {
                            "type": "word_batch_error",
                            "batch": batch_count,
                            "errors": batch_result.get("errors", []),
                        }
                    ],
                }

            merged_data = self._merge_extracted_data(
                merged_data,
                batch_result["data"],
            )

        if batch_count == 0:
            return {
                "status": "invalid",
                "data": None,
                "source_text": "",
                "ocr_text": "",
                "source_metadata": {},
                "errors": [
                    {
                        "type": "empty_word_document",
                        "message": "No text extracted from Word document.",
                    }
                ],
            }

        validation_result = self.validator.validate(
            merged_data
        )

        if not validation_result["valid"]:
            return {
                "status": "invalid",
                "data": validation_result.get("data"),
                "source_text": "\n\n".join(text_parts),
                "ocr_text": "",
                "source_metadata": {},
                "errors": validation_result.get("errors", []),
            }

        return {
            "status": "valid",
            "data": validation_result["data"],
            "source_text": "\n\n".join(text_parts),
            "ocr_text": "",
            "source_metadata": {
                "file_name": file_path.name,
                "route": "word_pipeline",
                "ocr_engine": None,
            },
            "errors": [],
        }

    def _process_structured_file(
        self,
        file_info,
    ):

        try:

            structured_data = (
                extract_structured_data(
                    file_info
                )
            )

            if not structured_data:

                return {
                    "status": "invalid",
                    "data": None,
                    "structured_data": None,
                    "structured_summary": None,
                    "errors": [
                        {
                            "type": (
                                "empty_structured_data"
                            ),
                            "message": (
                                "No structured data "
                                "extracted."
                            ),
                        }
                    ],
                }

            sheets = structured_data.get(
                "sheets",
                {},
            )

            if not sheets:

                return {
                    "status": "invalid",
                    "data": None,
                    "structured_data": (
                        structured_data
                    ),
                    "structured_summary": None,
                    "errors": [
                        {
                            "type": "empty_sheets",
                            "message": (
                                "No sheets found "
                                "in structured file."
                            ),
                        }
                    ],
                }

            sheet_summary = {}

            for (
                sheet_name,
                dataframe,
            ) in sheets.items():

                if not isinstance(
                    dataframe,
                    pd.DataFrame,
                ):

                    return {
                        "status": "invalid",
                        "data": None,
                        "structured_data": (
                            structured_data
                        ),
                        "structured_summary": None,
                        "errors": [
                            {
                                "type": (
                                    "invalid_sheet_data"
                                ),
                                "message": (
                                    f"Sheet '{sheet_name}' "
                                    "does not contain a "
                                    "pandas DataFrame."
                                ),
                            }
                        ],
                    }

                sheet_summary[
                    sheet_name
                ] = {
                    "rows": len(
                        dataframe
                    ),
                    "columns": len(
                        dataframe.columns
                    ),
                    "column_names": (
                        dataframe.columns.tolist()
                    ),
                }

            return {
                "status": "valid",
                "data": self._create_empty_data(),
                "structured_data": (
                    structured_data
                ),
                "structured_summary": (
                    sheet_summary
                ),
                "source_text": "",
                "ocr_text": "",
                "source_metadata": {
                    "file_name": Path(
                        file_info["file_path"]
                    ).name,
                    "route": "structured",
                    "ocr_engine": None,
                },
                "errors": [],
            }

        except Exception as error:

            return {
                "status": "error",
                "data": None,
                "structured_data": None,
                "structured_summary": None,
                "source_text": "",
                "ocr_text": "",
                "source_metadata": {},
                "errors": [
                    {
                        "type": (
                            "structured_processing_error"
                        ),
                        "message": str(error),
                    }
                ],
            }

    def _process_image(
        self,
        file_path,
    ):

        processed_image = process_image(
            file_path
        )

        if isinstance(
            processed_image,
            dict,
        ):

            image_path = (
                processed_image.get(
                    "processed_path"
                )
            )

            if image_path:

                ocr_result = (
                    self.ocr_router.process(
                        image_path,
                        engine=self.ocr_engine,
                        is_scanned_pdf=False,
                    )
                )

            else:

                ocr_result = (
                    self.ocr_router.process(
                        file_path,
                        engine=self.ocr_engine,
                        is_scanned_pdf=False,
                    )
                )

        else:

            ocr_result = (
                self.ocr_router.process(
                    processed_image,
                    engine=self.ocr_engine,
                    is_scanned_pdf=False,
                )
            )

        if not ocr_result.get("text"):
            return ""

        return ocr_result["text"]

    def _process_pdf_file(
        self,
        file_info,
    ):

        file_path = Path(
            file_info["file_path"]
        )

        pdf_info = detect_pdf_type(
            file_path
        )

        if pdf_info["pdf_type"] == "digital":

            return self._process_digital_pdf(
                file_path
            )

        return self._process_scanned_pdf(
            file_path
        )

    def _process_digital_pdf(
        self,
        file_path,
    ):

        merged_data = (
            self._create_empty_data()
        )

        batch_count = 0
        text_parts = []

        for batch_chunks in process_pdf_to_chunks(
            file_path
        ):

            batch_text = "\n\n".join(
                chunk["text"]
                for chunk in batch_chunks
                if chunk.get("text")
            )

            if not batch_text.strip():
                continue

            batch_count += 1
            print(f"       ↳ Processing PDF batch {batch_count}...", flush=True)

            text_parts.append(
                batch_text
            )

            batch_result = self.process_text(
                batch_text
            )

            if batch_result["status"] != "valid":

                return {
                    "status": (
                        batch_result["status"]
                    ),
                    "data": None,
                    "source_text": (
                        "\n\n".join(
                            text_parts
                        )
                    ),
                    "ocr_text": "",
                    "source_metadata": {},
                    "errors": [
                        {
                            "type": "pdf_batch_error",
                            "batch": batch_count,
                            "errors": (
                                batch_result[
                                    "errors"
                                ]
                            ),
                        }
                    ],
                }

            merged_data = (
                self._merge_extracted_data(
                    merged_data,
                    batch_result["data"],
                )
            )

        if batch_count == 0:

            return {
                "status": "invalid",
                "data": None,
                "source_text": "",
                "ocr_text": "",
                "source_metadata": {},
                "errors": [
                    {
                        "type": (
                            "empty_digital_pdf"
                        ),
                        "message": (
                            "No text batches were "
                            "extracted from the "
                            "digital PDF."
                        ),
                    }
                ],
            }

        validation_result = (
            self.validator.validate(
                merged_data
            )
        )

        if not validation_result["valid"]:

            return {
                "status": "invalid",
                "data": validation_result.get(
                    "data"
                ),
                "source_text": (
                    "\n\n".join(
                        text_parts
                    )
                ),
                "ocr_text": "",
                "source_metadata": {},
                "errors": (
                    validation_result.get(
                        "errors",
                        [],
                    )
                ),
            }

        return {
            "status": "valid",
            "data": validation_result["data"],
            "source_text": (
                "\n\n".join(
                    text_parts
                )
            ),
            "ocr_text": "",
            "source_metadata": {
                "file_name": file_path.name,
                "route": "digital_pdf",
                "ocr_engine": None,
            },
            "errors": [],
        }

    def _process_scanned_pdf(
        self,
        file_path,
    ):

        output_dir = (
            Path(PROCESSED_DIR)
            / "pdf_images"
        )

        text_parts = []
        confidence_values = []

        for page in convert_pdf_to_images(
            file_path,
            output_dir,
        ):

            ocr_result = (
                self.ocr_router.process(
                    page["image_path"],
                    engine=self.ocr_engine,
                    is_scanned_pdf=True,
                )
            )

            page_text = ocr_result.get(
                "text",
                "",
            )

            if page_text:
                text_parts.append(
                    page_text
                )

            confidence = ocr_result.get(
                "confidence"
            )

            if isinstance(
                confidence,
                (int, float),
            ):
                confidence_values.append(
                    float(confidence)
                )

        text = "\n\n".join(
            text_parts
        )

        if not text.strip():

            return {
                "status": "invalid",
                "data": None,
                "source_text": "",
                "ocr_text": "",
                "source_metadata": {},
                "errors": [
                    {
                        "type": (
                            "empty_scanned_pdf"
                        ),
                        "message": (
                            "No text extracted "
                            "from scanned PDF."
                        ),
                    }
                ],
            }

        result = self.process_text(
            text
        )

        if result["status"] != "valid":
            return result

        average_confidence = None

        if confidence_values:

            average_confidence = (
                sum(confidence_values)
                / len(confidence_values)
            )

        result["source_text"] = text
        result["ocr_text"] = text

        result["source_metadata"] = {
            "file_name": file_path.name,
            "route": "scanned_pdf",
            "ocr_engine": self.ocr_engine,
            "ocr_confidence": (
                average_confidence
            ),
        }

        return result

    def _build_source_document(
        self,
        file_path,
        data,
        source_metadata,
        source_text,
        ocr_text,
    ):

        file_path = Path(
            file_path
        )

        route = source_metadata.get(
            "route",
            "",
        )

        if route == "structured":
            return None

        if route == "image_pipeline":

            doc_type = "image"

        elif route == "digital_pdf":

            doc_type = "digital_pdf"

        elif route == "scanned_pdf":

            doc_type = "scanned_pdf"

        elif route == "word_pipeline":

            doc_type = "word"

        else:

            doc_type = (
                route
                or file_path.suffix.lower()
            )

        return {
            "file_name": file_path.name,
            "doc_type": doc_type,
            "ocr_text": (
                ocr_text
                if ocr_text
                else None
            ),
            "llm_json": json.dumps(
                data,
                ensure_ascii=False,
                default=str,
            ),
            "review_status": "auto_processed",
        }

    def _create_empty_data(self):

        return {
            "locations": [],
            "staff": [],
            "clients": [],
            "medical_history": [],
            "vitals": [],
            "lab_results": [],
            "medications": [],
            "services": [],
            "appointments": [],
            "treatment_records": [],
            "consents": [],
            "photos": [],
            "invoices": [],
            "invoice_items": [],
            "payments": [],
            "packages": [],
            "client_packages": [],
            "products": [],
            "source_documents": [],
        }

    def _merge_extracted_data(
        self,
        merged_data,
        batch_data,
    ):

        for table in merged_data:

            records = batch_data.get(
                table,
                [],
            )

            if not isinstance(
                records,
                list,
            ):
                continue

            merged_data[
                table
            ].extend(records)

        return merged_data
```

<a id='file-src-utils-py'></a>
### الملف: `src\utils.py`
**المسار الكامل:** `E:\ZaWolf_project\src\utils.py`

```python
import psutil

from config.settings import BATCH_MEMORY_SAFETY_RATIO, MAX_BATCH_TEXT_SIZE
from langchain_text_splitters import RecursiveCharacterTextSplitter


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=300,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ]
)


def get_dynamic_batch_limit():
    memory = psutil.virtual_memory()

    available_bytes = memory.available
    memory_budget = int(
        available_bytes * BATCH_MEMORY_SAFETY_RATIO
    )

    return {
        "available_bytes": available_bytes,
        "memory_budget_bytes": memory_budget
    }


def batch_text_units(text_units):
    batch = []
    batch_size_bytes = 0
    batch_text_size = 0

    for unit in text_units:
        text = unit["text"]

        unit_size_bytes = len(text.encode("utf-8"))
        unit_text_size = len(text)

        memory_limit = get_dynamic_batch_limit()
        memory_budget = memory_limit["memory_budget_bytes"]

        exceeds_text_limit = (
            batch_text_size + unit_text_size > MAX_BATCH_TEXT_SIZE
        )

        exceeds_memory_limit = (
            batch_size_bytes + unit_size_bytes > memory_budget
        )

        if batch and (
            exceeds_text_limit or exceeds_memory_limit
        ):
            yield batch

            batch = []
            batch_size_bytes = 0
            batch_text_size = 0

        batch.append(unit)

        batch_size_bytes += unit_size_bytes
        batch_text_size += unit_text_size

    if batch:
        yield batch


def create_text_chunks(text_batch, file_name):
    chunks = []

    combined_text = "\n\n".join(
        unit["text"]
        for unit in text_batch
        if unit["text"]
    )

    if not combined_text:
        return chunks

    text_chunks = text_splitter.split_text(
        combined_text
    )

    for chunk_index, chunk_text in enumerate(
        text_chunks,
        start=1
    ):
        chunks.append({
            "file_name": file_name,
            "chunk_index": chunk_index,
            "text": chunk_text,
            "text_length": len(chunk_text)
        })

    return chunks


def process_text_units(text_units, file_name):
    for text_batch in batch_text_units(text_units):
        yield create_text_chunks(
            text_batch,
            file_name
        )

def create_content_record(
    file_name,
    file_type,
    content,
    source_type=None,
    source_number=None
):
    return {
        "file_name": file_name,
        "file_type": file_type,
        "source_type": source_type,
        "source_number": source_number,
        "content_type": "text",
        "content": content
    }        
```

<a id='file-src-ingestion-file_detector-py'></a>
### الملف: `src\ingestion\file_detector.py`
**المسار الكامل:** `E:\ZaWolf_project\src\ingestion\file_detector.py`

```python
from pathlib import Path

from config.settings import INPUT_DIR, SUPPORTED_EXTENSIONS


def get_input_files():
    return [
        file_path
        for file_path in INPUT_DIR.iterdir()
        if file_path.is_file()
    ]


def detect_file_type(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    extension = file_path.suffix.lower()
    file_type = SUPPORTED_EXTENSIONS.get(extension)

    return {
        "file_name": file_path.name,
        "file_path": str(file_path),
        "extension": extension,
        "file_type": file_type or "unsupported",
        "supported": file_type is not None
    }
```

<a id='file-src-ingestion-router-py'></a>
### الملف: `src\ingestion\router.py`
**المسار الكامل:** `E:\ZaWolf_project\src\ingestion\router.py`

```python
def route_file(file_info):
    file_type = file_info["file_type"]

    routes = {
        "pdf": "pdf_pipeline",
        "image": "image_pipeline",
        "excel": "excel_pipeline",
        "csv": "csv_pipeline",
        "word": "word_pipeline"
    }

    return routes.get(file_type, "unsupported")
```

<a id='file-src-processors-pdf_processor-py'></a>
### الملف: `src\processors\pdf_processor.py`
**المسار الكامل:** `E:\ZaWolf_project\src\processors\pdf_processor.py`

```python
from pathlib import Path

import pymupdf as fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.settings import MAX_BATCH_TEXT_SIZE
from src.utils import get_dynamic_batch_limit


def detect_pdf_type(file_path):
    file_path = Path(file_path)

    if file_path.suffix.lower() != ".pdf":
        raise ValueError("The provided file is not a PDF file.")

    document = fitz.open(file_path)

    try:
        text_length = sum(
            len(page.get_text("text").strip())
            for page in document
        )
    finally:
        document.close()

    pdf_type = "digital" if text_length > 0 else "scanned"

    return {
        "file_name": file_path.name,
        "file_path": str(file_path),
        "pdf_type": pdf_type,
        "text_length": text_length
    }


def extract_pdf_pages(file_path):
    file_path = Path(file_path)

    if file_path.suffix.lower() != ".pdf":
        raise ValueError("The provided file is not a PDF file.")

    document = fitz.open(file_path)

    try:
        batch = []
        batch_size_bytes = 0
        batch_text_size = 0

        for page_number, page in enumerate(document, start=1):
            page_text = page.get_text("text").strip()

            if not page_text:
                continue

            page_size_bytes = len(page_text.encode("utf-8"))
            page_text_size = len(page_text)

            memory_limit = get_dynamic_batch_limit()
            memory_budget = memory_limit["memory_budget_bytes"]

            exceeds_text_limit = (
                batch_text_size + page_text_size > MAX_BATCH_TEXT_SIZE
            )

            exceeds_memory_limit = (
                batch_size_bytes + page_size_bytes > memory_budget
            )

            if batch and (exceeds_text_limit or exceeds_memory_limit):
                yield batch

                batch = []
                batch_size_bytes = 0
                batch_text_size = 0

            batch.append({
                "file_name": file_path.name,
                "file_type": "pdf",
                "source_type": "page",
                "source_number": page_number,
                "text": page_text,
                "text_length": page_text_size
            })

            batch_size_bytes += page_size_bytes
            batch_text_size += page_text_size

        if batch:
            yield batch

    finally:
        document.close()


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=300,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ]
)


def create_contextual_chunks(page_batch, file_name):
    chunks = []

    page_texts = [
        page_data["text"]
        for page_data in page_batch
        if page_data["text"]
    ]

    if not page_texts:
        return chunks

    combined_text = "\n\n".join(page_texts)

    page_chunks = text_splitter.split_text(
        combined_text
    )

    for chunk_index, chunk_text in enumerate(
        page_chunks,
        start=1
    ):
        chunks.append({
            "file_name": file_name,
            "chunk_index": chunk_index,
            "text": chunk_text,
            "text_length": len(chunk_text)
        })

    return chunks


def process_pdf_to_chunks(file_path):
    for page_batch in extract_pdf_pages(file_path):
        yield create_contextual_chunks(
            page_batch,
            Path(file_path).name
        )


def convert_pdf_to_images(file_path, output_dir):
    file_path = Path(file_path)
    output_dir = Path(output_dir)

    if file_path.suffix.lower() != ".pdf":
        raise ValueError("The provided file is not a PDF file.")

    output_dir.mkdir(parents=True, exist_ok=True)

    document = fitz.open(file_path)

    try:
        for page_number, page in enumerate(document, start=1):
            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(1, 1),
                alpha=False
            )

            image_path = (
                output_dir /
                f"{file_path.stem}_page_{page_number}.png"
            )

            pixmap.save(str(image_path))

            yield {
                "file_name": file_path.name,
                "page_number": page_number,
                "image_path": str(image_path)
            }

    finally:
        document.close()
```

<a id='file-src-processors-word_processor-py'></a>
### الملف: `src\processors\word_processor.py`
**المسار الكامل:** `E:\ZaWolf_project\src\processors\word_processor.py`

```python
from pathlib import Path

from docx import Document

from src.utils import process_text_units


def extract_word_content(file_path):
    file_path = Path(file_path)

    if file_path.suffix.lower() != ".docx":
        raise ValueError(
            "The provided file is not a DOCX file."
        )

    document = Document(file_path)

    content = []

    for paragraph_number, paragraph in enumerate(
        document.paragraphs,
        start=1
    ):
        text = paragraph.text.strip()

        if text:
            content.append({
                "source_type": "paragraph",
                "source_number": paragraph_number,
                "text": text,
                "text_length": len(text)
            })

    for table_number, table in enumerate(
        document.tables,
        start=1
    ):
        rows = []

        for row in table.rows:
            cells = [
                cell.text.strip()
                for cell in row.cells
            ]

            if any(cells):
                rows.append(cells)

        if rows:
            table_text = "\n".join(
                " | ".join(row)
                for row in rows
            )

            content.append({
                "source_type": "table",
                "source_number": table_number,
                "text": table_text,
                "text_length": len(table_text)
            })

    return content


def process_word(file_path):
    file_path = Path(file_path)

    text_units = extract_word_content(file_path)

    yield from process_text_units(
        text_units,
        file_path.name
    )
```

<a id='file-src-processors-structured_processor-py'></a>
### الملف: `src\processors\structured_processor.py`
**المسار الكامل:** `E:\ZaWolf_project\src\processors\structured_processor.py`

```python
from pathlib import Path

import pandas as pd


def extract_structured_data(file_info):
    file_path = Path(file_info["file_path"])
    file_type = file_info["file_type"]

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if file_type == "csv":
        sheets = {
            "default": pd.read_csv(file_path)
        }

    elif file_type == "excel":
        sheets = pd.read_excel(
            file_path,
            sheet_name=None
        )

    else:
        raise ValueError(
            "The provided file is not an Excel or CSV file."
        )

    return {
        "file_name": file_path.name,
        "file_path": str(file_path),
        "file_type": file_type,
        "content_type": "structured",
        "sheets": sheets
    }
```

<a id='file-src-processors-image_processor-py'></a>
### الملف: `src\processors\image_processor.py`
**المسار الكامل:** `E:\ZaWolf_project\src\processors\image_processor.py`

```python
from pathlib import Path

from PIL import Image, ImageOps

from config.settings import (
    SUPPORTED_IMAGE_EXTENSIONS,
    IMAGE_PROCESSED_DIR
)


def load_and_validate_image(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if file_path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
        raise ValueError(
            "The provided file is not a supported image format."
        )

    try:
        image = Image.open(file_path)
        image.load()
    except Exception as error:
        raise ValueError(
            f"Invalid or corrupted image: {error}"
        )

    return {
        "file_name": file_path.name,
        "file_path": str(file_path),
        "format": image.format,
        "mode": image.mode,
        "width": image.width,
        "height": image.height
    }


def preprocess_image(file_path, output_path=None):
    file_path = Path(file_path)

    image = Image.open(file_path)
    image.load()

    image = ImageOps.exif_transpose(image)
    image = image.convert("L")
    image = ImageOps.autocontrast(image)

    if output_path is not None:
        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        image.save(output_path)

    return image


def process_image(file_path):
    file_path = Path(file_path)

    load_and_validate_image(file_path)

    output_path = (
        IMAGE_PROCESSED_DIR /
        f"{file_path.stem}_processed.png"
    )

    image = preprocess_image(
        file_path,
        output_path
    )

    return {
        "file_name": file_path.name,
        "file_type": "image",
        "content_type": "image",
        "original_path": str(file_path),
        "processed_path": str(output_path),
        "width": image.width,
        "height": image.height,
        "mode": image.mode
    }
```

<a id='file-src-processors-extraction_schema-py'></a>
### الملف: `src\processors\extraction_schema.py`
**المسار الكامل:** `E:\ZaWolf_project\src\processors\extraction_schema.py`

```python
from datetime import datetime


def create_unified_extraction(
    file_name,
    file_type,
    content_type,
    sources,
    metadata=None
):
    return {
        "file": {
            "name": file_name,
            "type": file_type
        },
        "content_type": content_type,
        "sources": sources,
        "metadata": metadata or {},
        "created_at": datetime.now().isoformat()
    }


def create_text_source(
    source_number,
    text,
    source_type="text",
    language=None,
    confidence=None,
    ocr_engine=None
):
    source = {
        "source_type": source_type,
        "source_number": source_number,
        "raw_text": text
    }

    if language is not None:
        source["language"] = language

    if confidence is not None:
        source["confidence"] = confidence

    if ocr_engine is not None:
        source["ocr_engine"] = ocr_engine

    return source


def create_structured_source(
    source_number,
    data,
    source_type="structured"
):
    return {
        "source_type": source_type,
        "source_number": source_number,
        "raw_data": data
    }
```

<a id='file-src-ocr-device-py'></a>
### الملف: `src\ocr\device.py`
**المسار الكامل:** `E:\ZaWolf_project\src\ocr\device.py`

```python
import torch


def get_device(preference="auto"):
    if preference == "cpu":
        return "cpu"

    if preference == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is not available.")
        return "cuda"

    return "cuda" if torch.cuda.is_available() else "cpu"
```

<a id='file-src-ocr-ocr_engine-py'></a>
### الملف: `src\ocr\ocr_engine.py`
**المسار الكامل:** `E:\ZaWolf_project\src\ocr\ocr_engine.py`

```python
import os

os.environ["FLAGS_enable_pir_api"] = "0"

from pathlib import Path
from paddleocr import PaddleOCR

from src.ocr.ocr_utils import (
    validate_image_path,
    parse_paddle_result,
    create_ocr_record
)


class OCREngine:

    def __init__(self, lang="ar"):
        self.lang = lang
        self.engine = PaddleOCR(
            lang=lang,
            enable_mkldnn=False
        )

    def extract_text(self, image_path):
        image_path = validate_image_path(image_path)

        result = self.engine.predict(
            str(image_path)
        )

        parsed_result = parse_paddle_result(result)

        return create_ocr_record(
            file_name=image_path.name,
            source_type="image",
            source_number=1,
            text=parsed_result["text"],
            ocr_engine="PaddleOCR",
            language=self.lang,
            confidence=parsed_result["confidence"]
        )
```

<a id='file-src-ocr-handwriting_ocr-py'></a>
### الملف: `src\ocr\handwriting_ocr.py`
**المسار الكامل:** `E:\ZaWolf_project\src\ocr\handwriting_ocr.py`

```python
from pathlib import Path

import torch
from PIL import Image
from transformers import (
    AutoProcessor,
    Qwen2_5_VLForConditionalGeneration
)


class HandwritingOCREngine:

    def __init__(self, device="auto"):
        self.device = self._get_device(device)

        self.model_name = (
            "sherif1313/"
            "Arabic-handwritten-OCR-4bit-Qwen2.5-VL-3B-v3"
        )

        self.processor = AutoProcessor.from_pretrained(
            self.model_name
        )

        if self.device == "cuda":
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                self.model_name,
                device_map="cuda"
            )
        else:
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                self.model_name,
                device_map="cpu"
            )

        self.model.eval()

    @staticmethod
    def _get_device(device):
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"

        if device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError(
                "CUDA requested but no CUDA GPU is available."
            )

        if device not in ["cuda", "cpu"]:
            raise ValueError(
                "Device must be 'auto', 'cuda', or 'cpu'."
            )

        return device

    def extract_text(self, image_path):
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        if not image_path.is_file():
            raise ValueError(
                f"Path is not a file: {image_path}"
            )

        image = Image.open(image_path).convert("RGB")

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": image
                    },
                    {
                        "type": "text",
                        "text": (
                            "Transcribe all handwritten text in this image "
                            "exactly as it appears. Preserve medicine names, "
                            "numbers, dosages, units, and instructions. "
                            "Do not add information that is not visible."
                        )
                    }
                ]
            }
        ]

        text_prompt = self.processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.processor(
            text=[text_prompt],
            images=[image],
            return_tensors="pt"
        )

        target_device = torch.device(self.device)

        inputs = {
            key: value.to(target_device)
            if hasattr(value, "to")
            else value
            for key, value in inputs.items()
        }

        with torch.inference_mode():
            generated_ids = self.model.generate(
                **inputs,
                max_new_tokens=512
            )

        input_length = inputs["input_ids"].shape[1]

        generated_text = self.processor.batch_decode(
            generated_ids[:, input_length:],
            skip_special_tokens=True
        )[0].strip()

        return {
            "file_name": image_path.name,
            "source_type": "image",
            "source_number": 1,
            "ocr_engine": "Qwen2.5-VL-3B-Handwriting-OCR",
            "language": "ar/en",
            "text": generated_text,
            "device": self.device,
            "status": "success"
        }
```

<a id='file-src-ocr-ocr_router-py'></a>
### الملف: `src\ocr\ocr_router.py`
**المسار الكامل:** `E:\ZaWolf_project\src\ocr\ocr_router.py`

```python
from src.ocr.ocr_engine import OCREngine
from src.ocr.handwriting_ocr import HandwritingOCREngine
from src.ocr.device import get_device


class OCRRouter:

    def __init__(self, device="auto"):
        self.device = get_device(device)
        self.qwen_engine = None
        self.printed_engine = None

    def _get_qwen_engine(self):
        if self.qwen_engine is None:
            self.qwen_engine = HandwritingOCREngine(
                device=self.device
            )

        return self.qwen_engine

    def _get_printed_engine(self):
        if self.printed_engine is None:
            self.printed_engine = OCREngine(lang="ar")

        return self.printed_engine

    def process(self, image_path, engine="auto", is_scanned_pdf=False):
        if engine == "paddle":
            return self._get_printed_engine().extract_text(image_path)

        if engine == "qwen":
            return self._get_qwen_engine().extract_text(image_path)

        if engine == "auto":
            # Pages from multi-page scanned PDFs default to PaddleOCR for high throughput
            if is_scanned_pdf:
                return self._get_printed_engine().extract_text(image_path)

            # Standalone images: fast check with printed OCR pass
            printed_result = self._get_printed_engine().extract_text(image_path)
            text = printed_result.get("text", "").strip()
            confidence = printed_result.get("confidence", 0.0)

            # If substantial printed text is detected with solid confidence, return it immediately
            if len(text) >= 40 and confidence >= 0.70:
                return printed_result

            # If text is sparse, low-confidence, or handwritten prescription, route to Qwen-VL
            try:
                qwen_result = self._get_qwen_engine().extract_text(image_path)
                qwen_text = qwen_result.get("text", "").strip()
                if qwen_text:
                    return qwen_result
            except Exception:
                pass

            return printed_result

        raise ValueError(
            "Engine must be 'auto', 'qwen', or 'paddle'."
        )
```

<a id='file-src-ocr-ocr_utils-py'></a>
### الملف: `src\ocr\ocr_utils.py`
**المسار الكامل:** `E:\ZaWolf_project\src\ocr\ocr_utils.py`

```python
from pathlib import Path


def validate_image_path(image_path):
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    if not image_path.is_file():
        raise ValueError(
            f"Path is not a file: {image_path}"
        )

    return image_path


def normalize_ocr_text(text):
    if text is None:
        return ""

    return " ".join(str(text).split())


def parse_paddle_result(result):
    texts = []
    scores = []

    for page_result in result:
        data = page_result

        if hasattr(data, "rec_texts"):
            texts.extend(data.rec_texts)
            scores.extend(data.rec_scores)

        elif isinstance(data, dict):
            texts.extend(data.get("rec_texts", []))
            scores.extend(data.get("rec_scores", []))

    clean_texts = [
        normalize_ocr_text(text)
        for text in texts
        if normalize_ocr_text(text)
    ]

    valid_scores = [
        float(score)
        for score in scores
        if score is not None
    ]

    full_text = "\n".join(clean_texts)

    confidence = (
        sum(valid_scores) / len(valid_scores)
        if valid_scores
        else 0.0
    )

    return {
        "text": full_text,
        "confidence": confidence
    }



def create_ocr_record(
    file_name,
    source_type,
    source_number,
    text,
    ocr_engine,
    language="ar",
    confidence=0.0
):
    return {
        "file_name": file_name,
        "source_type": source_type,
        "source_number": source_number,
        "ocr_engine": ocr_engine,
        "language": language,
        "text": normalize_ocr_text(text),
        "confidence": confidence,
        "status": "success"
    }
```

<a id='file-src-llm-local_llm-py'></a>
### الملف: `src\llm\local_llm.py`
**المسار الكامل:** `E:\ZaWolf_project\src\llm\local_llm.py`

```python
import json
import os
import requests
import requests.adapters


def get_optimal_thread_count():
    try:
        import psutil
        physical = psutil.cpu_count(logical=False)
        if physical and physical > 0:
            return physical
    except Exception:
        pass
    logical = os.cpu_count() or 4
    return max(1, logical // 2 if logical > 2 else logical)


class LocalLLM:
    def __init__(
        self,
        model="qwen3:latest",
        base_url="http://localhost:11434",
        timeout=600
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = None
        self.threads = get_optimal_thread_count()

    def _get_session(self):
        if self._session is None:
            self._session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=1,
                pool_maxsize=2,
                max_retries=1
            )
            self._session.mount("http://", adapter)
            self._session.mount("https://", adapter)
        return self._session

    def close(self):
        """Explicitly closes the HTTP session and frees socket handles immediately."""
        if self._session is not None:
            try:
                self._session.close()
            except Exception:
                pass
            self._session = None

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def generate(self, prompt, system_prompt=None):
        print("\n===== LLM DEBUG =====")
        print(f"Model: {self.model}")
        print(f"Threads: {self.threads} (auto-detected)")
        print(f"Prompt length: {len(prompt):,} chars")

        if system_prompt:
            print(f"System prompt length: {len(system_prompt):,} chars")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "think": False,
            "options": {
                "num_ctx": 16384,
                "num_predict": 2048,
                "temperature": 0.0,
                "num_thread": self.threads
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        response = self._get_session().post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.timeout
        )

        response.raise_for_status()

        result = response.json()

        if "response" not in result:
            raise ValueError("LLM response field is missing.")

        response_text = result["response"]

        print(f"Response length: {len(response_text):,} chars")
        print("===== END LLM DEBUG =====\n")

        return response_text

    def generate_json(self, prompt, system_prompt=None):
        response_text = self.generate(
            prompt=prompt,
            system_prompt=system_prompt
        )

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as error:
            print("\n===== INVALID JSON RESPONSE =====")
            print(response_text)
            print("===== END INVALID JSON RESPONSE =====\n")

            raise ValueError(
                f"LLM returned invalid JSON: {error}"
            ) from error
```

<a id='file-src-llm-llm_processor-py'></a>
### الملف: `src\llm\llm_processor.py`
**المسار الكامل:** `E:\ZaWolf_project\src\llm\llm_processor.py`

```python
import json
from datetime import datetime

from src.llm.local_llm import LocalLLM
from src.llm.llm_schema import LLMExtractionResult
from src.validation.extraction_guard import ExtractionGuard


class LLMProcessor:

    def __init__(
        self,
        model="qwen3:latest",
        base_url="http://localhost:11434",
        timeout=600,
    ):
        self.llm = LocalLLM(
            model=model,
            base_url=base_url,
            timeout=timeout,
        )

        self.guard = ExtractionGuard()

    def build_prompt(self, text):
        return f"""You are a clinical document information extraction system. Extract ONLY explicitly stated facts into the exact JSON schema below.

STRICT CONSTRAINTS:
- NEVER hallucinate, invent, or extrapolate unmentioned entities.
- If an entity or attribute is not explicitly in the text, return null (or [] for arrays).
- Never invent patient names, doctors, locations, appointments, diagnoses, or invoices.
- Dates: Use YYYY-MM-DD only when day, month, and year are clearly given; otherwise null. Do not convert durations (e.g. "لمدة أسبوع") into dates.
- Numbers: Preserve original values accurately.

MEDICATION EXTRACTION:
- Extract each explicitly named medication as a separate record. Preserve exact medication_name, dosage, and frequency.
- Only associate dosage and frequency appearing in the text immediately following the medication name.
- Do not mix attributes between different medications.

OUTPUT RULES:
Return ONLY valid JSON (no markdown fences, no conversational text, no comments). Schema:
{{
    "locations": [],
    "staff": [],
    "clients": [],
    "medical_history": [],
    "vitals": [],
    "lab_results": [],
    "medications": [],
    "services": [],
    "appointments": [],
    "treatment_records": [],
    "consents": [],
    "photos": [],
    "invoices": [],
    "invoice_items": [],
    "payments": [],
    "packages": [],
    "client_packages": [],
    "products": [],
    "source_documents": []
}}

Each entity must contain only schema-supported fields (e.g. medications: medication_name, dosage, frequency; vitals: blood_pressure, heart_rate, temperature, weight; locations: name, address, phone).

INPUT TEXT:
{text}
"""

    def _parse_json(self, response_text):

        response_text = response_text.strip()

        if response_text.startswith("```"):

            lines = response_text.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            response_text = "\n".join(lines).strip()

        try:
            return json.loads(response_text)

        except json.JSONDecodeError as error:

            raise ValueError(
                f"LLM returned invalid JSON: {error}"
            ) from error

    def _normalize_numeric_values(self, data):

        numeric_fields = {
            "clients": [
                "id",
            ],
            "vitals": [
                "weight",
                "height",
                "temperature",
                "heart_rate",
                "blood_pressure_systolic",
                "blood_pressure_diastolic",
                "oxygen_saturation",
            ],
            "lab_results": [
                "result_value",
                "reference_min",
                "reference_max",
            ],
            "invoices": [
                "subtotal",
                "discount",
                "tax",
                "total",
            ],
            "invoice_items": [
                "quantity",
                "unit_price",
                "total",
            ],
            "payments": [
                "amount",
            ],
        }

        for table, fields in numeric_fields.items():

            records = data.get(table, [])

            if not isinstance(records, list):
                continue

            for record in records:

                if not isinstance(record, dict):
                    continue

                for field in fields:

                    value = record.get(field)

                    if value is None:
                        continue

                    if isinstance(value, (int, float)):
                        continue

                    if not isinstance(value, str):
                        record[field] = None
                        continue

                    value = value.strip()

                    if value == "":
                        record[field] = None
                        continue

                    try:

                        if "." in value:
                            record[field] = float(value)
                        else:
                            record[field] = int(value)

                    except ValueError:

                        record[field] = None

        return data

    def _normalize_string_values(self, data):

        string_fields = {
            "locations": [
                "name",
                "address",
                "phone",
            ],
            "staff": [
                "first_name",
                "last_name",
                "role",
                "specialization",
                "phone",
                "email",
            ],
            "clients": [
                "first_name",
                "last_name",
                "gender",
                "phone",
                "email",
                "address",
            ],
            "medical_history": [
                "condition",
                "diagnosis",
                "notes",
            ],
            "vitals": [
                "blood_pressure",
                "notes",
            ],
            "lab_results": [
                "test_name",
                "result",
                "unit",
                "reference_range",
                "notes",
            ],
            "medications": [
                "medication_name",
                "dosage",
                "frequency",
            ],
            "services": [
                "name",
                "description",
            ],
            "appointments": [
                "status",
                "notes",
            ],
            "treatment_records": [
                "treatment_name",
                "description",
                "notes",
            ],
            "consents": [
                "consent_type",
                "status",
                "notes",
            ],
            "photos": [
                "file_path",
                "description",
            ],
            "invoices": [
                "invoice_number",
                "status",
                "notes",
            ],
            "invoice_items": [
                "description",
            ],
            "payments": [
                "payment_method",
                "status",
                "transaction_reference",
            ],
            "packages": [
                "name",
                "description",
            ],
            "client_packages": [
                "status",
            ],
            "products": [
                "name",
                "description",
                "category",
            ],
            "source_documents": [
                "file_name",
                "file_type",
                "file_path",
            ],
        }

        for table, fields in string_fields.items():

            records = data.get(table, [])

            if not isinstance(records, list):
                continue

            for record in records:

                if not isinstance(record, dict):
                    continue

                for field in fields:

                    value = record.get(field)

                    if value is None:
                        continue

                    if not isinstance(value, str):
                        record[field] = str(value)

        return data

    def _normalize_dates(self, data):

        date_fields = {
            "clients": [
                "dob",
            ],
            "medical_history": [
                "recorded_at",
            ],
            "vitals": [
                "recorded_at",
            ],
            "lab_results": [
                "test_date",
            ],
            "medications": [
                "start_date",
                "end_date",
            ],
            "invoices": [
                "issue_date",
            ],
            "treatment_records": [
                "expiry_date",
            ],
        }

        datetime_fields = {
            "appointments": [
                "start_at",
                "end_at",
            ],
            "consents": [
                "signed_at",
            ],
            "photos": [
                "taken_at",
            ],
            "payments": [
                "paid_at",
            ],
        }

        for table, fields in date_fields.items():

            records = data.get(table, [])

            if not isinstance(records, list):
                continue

            for record in records:

                if not isinstance(record, dict):
                    continue

                for field in fields:

                    value = record.get(field)

                    if value is None:
                        record[field] = None
                        continue

                    if not isinstance(value, str):
                        record[field] = None
                        continue

                    value = value.strip()

                    if value == "":
                        record[field] = None
                        continue

                    try:

                        parsed_date = datetime.strptime(
                            value,
                            "%Y-%m-%d",
                        )

                        record[field] = parsed_date.strftime(
                            "%Y-%m-%d"
                        )

                    except ValueError:

                        record[field] = None

        for table, fields in datetime_fields.items():

            records = data.get(table, [])

            if not isinstance(records, list):
                continue

            for record in records:

                if not isinstance(record, dict):
                    continue

                for field in fields:

                    value = record.get(field)

                    if value is None:
                        record[field] = None
                        continue

                    if not isinstance(value, str):
                        record[field] = None
                        continue

                    value = value.strip()

                    if value == "":
                        record[field] = None
                        continue

                    valid_formats = [
                        "%Y-%m-%d %H:%M:%S",
                        "%Y-%m-%d %H:%M",
                        "%Y-%m-%dT%H:%M:%S",
                        "%Y-%m-%dT%H:%M",
                    ]

                    normalized = None

                    for date_format in valid_formats:

                        try:

                            parsed_datetime = datetime.strptime(
                                value,
                                date_format,
                            )

                            normalized = parsed_datetime.strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )

                            break

                        except ValueError:
                            continue

                    record[field] = normalized

        return data

    def process(self, text):

        prompt = self.build_prompt(text)

        raw_response = self.llm.generate(
            prompt
        )

        data = self._parse_json(
            raw_response
        )

        data = self._normalize_numeric_values(
            data
        )

        data = self._normalize_string_values(
            data
        )

        data = self._normalize_dates(
            data
        )

        data = self.guard.apply(
            data,
            text
        )

        validated = LLMExtractionResult.model_validate(
            data
        )

        return validated.model_dump()

    def close(self):
        if hasattr(self, "llm") and self.llm:
            self.llm.close()
```

<a id='file-src-llm-llm_schema-py'></a>
### الملف: `src\llm\llm_schema.py`
**المسار الكامل:** `E:\ZaWolf_project\src\llm\llm_schema.py`

```python
from typing import Optional, List
from pydantic import BaseModel


class LocationData(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None


class StaffData(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    license_no: Optional[str] = None
    location_name: Optional[str] = None
    is_active: Optional[bool] = None


class ClientData(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    lead_source: Optional[str] = None
    medical_alerts: Optional[str] = None
    opt_in_sms: Optional[bool] = None


class MedicalHistoryData(BaseModel):
    type: Optional[str] = None
    name: Optional[str] = None
    notes: Optional[str] = None
    recorded_at: Optional[str] = None


class VitalData(BaseModel):
    blood_pressure: Optional[str] = None
    heart_rate: Optional[float] = None
    temperature: Optional[float] = None
    weight: Optional[float] = None
    recorded_at: Optional[str] = None


class LabResultData(BaseModel):
    test_name: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    test_date: Optional[str] = None


class MedicationData(BaseModel):
    medication_name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ServiceData(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    duration_min: Optional[int] = None
    price: Optional[float] = None


class AppointmentData(BaseModel):
    client_name: Optional[str] = None
    staff_name: Optional[str] = None
    location_name: Optional[str] = None
    service_name: Optional[str] = None
    room: Optional[str] = None
    start_at: Optional[str] = None
    end_at: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class TreatmentRecordData(BaseModel):
    appointment_id: Optional[int] = None
    product_name: Optional[str] = None
    units: Optional[float] = None
    lot_number: Optional[str] = None
    expiry_date: Optional[str] = None
    area: Optional[str] = None
    injection_sites: Optional[str] = None
    depth: Optional[str] = None
    device_settings: Optional[str] = None
    skin_response: Optional[str] = None
    aftercare: Optional[str] = None


class ConsentData(BaseModel):
    appointment_id: Optional[int] = None
    consent_type: Optional[str] = None
    signed_at: Optional[str] = None
    file_ref: Optional[str] = None


class PhotoData(BaseModel):
    treatment_id: Optional[int] = None
    type: Optional[str] = None
    taken_at: Optional[str] = None
    file_ref: Optional[str] = None


class InvoiceData(BaseModel):
    appointment_id: Optional[int] = None
    issue_date: Optional[str] = None
    subtotal: Optional[float] = None
    discount: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None
    status: Optional[str] = None


class InvoiceItemData(BaseModel):
    invoice_id: Optional[int] = None
    item_type: Optional[str] = None
    item_id: Optional[int] = None
    description: Optional[str] = None
    qty: Optional[float] = None
    unit_price: Optional[float] = None
    line_total: Optional[float] = None


class PaymentData(BaseModel):
    invoice_id: Optional[int] = None
    amount: Optional[float] = None
    method: Optional[str] = None
    paid_at: Optional[str] = None
    reference: Optional[str] = None


class PackageData(BaseModel):
    name: Optional[str] = None
    sessions_count: Optional[int] = None
    price: Optional[float] = None
    validity_days: Optional[int] = None


class ClientPackageData(BaseModel):
    package_name: Optional[str] = None
    remaining_sessions: Optional[int] = None
    expires_at: Optional[str] = None


class ProductData(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    type: Optional[str] = None
    unit: Optional[str] = None
    stock_qty: Optional[float] = None
    cost: Optional[float] = None
    price: Optional[float] = None


class SourceDocumentData(BaseModel):
    file_name: Optional[str] = None
    doc_type: Optional[str] = None
    ocr_text: Optional[str] = None
    llm_json: Optional[dict] = None
    confidence: Optional[float] = None
    review_status: Optional[str] = None


class LLMExtractionResult(BaseModel):
    locations: List[LocationData] = []
    staff: List[StaffData] = []
    clients: List[ClientData] = []
    medical_history: List[MedicalHistoryData] = []
    vitals: List[VitalData] = []
    lab_results: List[LabResultData] = []
    medications: List[MedicationData] = []
    services: List[ServiceData] = []
    appointments: List[AppointmentData] = []
    treatment_records: List[TreatmentRecordData] = []
    consents: List[ConsentData] = []
    photos: List[PhotoData] = []
    invoices: List[InvoiceData] = []
    invoice_items: List[InvoiceItemData] = []
    payments: List[PaymentData] = []
    packages: List[PackageData] = []
    client_packages: List[ClientPackageData] = []
    products: List[ProductData] = []
    source_documents: List[SourceDocumentData] = []
```

<a id='file-src-validation-extraction_guard-py'></a>
### الملف: `src\validation\extraction_guard.py`
**المسار الكامل:** `E:\ZaWolf_project\src\validation\extraction_guard.py`

```python
class ExtractionGuard:
    def apply(self, data, text):
        self._guard_prescription_entities(data, text)
        self._guard_empty_entities(data)
        return data

    def _guard_prescription_entities(self, data, text):
        text_lower = text.lower()

        prescription_keywords = [
            "prescription",
            "prescription:",
            "rx",
            "دواء",
            "ادوية",
            "دواء",
            "روشتة",
            "علاج",
            "مرات يوميا",
            "مرة يوميا",
            "بعد الأكل",
            "قبل الأكل",
            "قطرة",
            "قرص",
            "كبسولة",
            "مرهم",
        ]

        is_prescription = any(
            keyword in text_lower
            for keyword in prescription_keywords
        )

        if not is_prescription:
            return

        allowed_tables = {
            "medications",
        }

        protected_tables = [
            "locations",
            "staff",
            "clients",
            "medical_history",
            "vitals",
            "lab_results",
            "services",
            "appointments",
            "treatment_records",
            "consents",
            "photos",
            "invoices",
            "invoice_items",
            "payments",
            "packages",
            "client_packages",
            "products",
        ]

        for table in protected_tables:
            if table not in allowed_tables:
                data[table] = []

    def _guard_empty_entities(self, data):
        for table, records in data.items():
            if not isinstance(records, list):
                continue

            cleaned_records = []

            for record in records:
                if not isinstance(record, dict):
                    continue

                if any(
                    value is not None and value != ""
                    for value in record.values()
                ):
                    cleaned_records.append(record)

            data[table] = cleaned_records
```

<a id='file-src-validation-validator-py'></a>
### الملف: `src\validation\validator.py`
**المسار الكامل:** `E:\ZaWolf_project\src\validation\validator.py`

```python
from pydantic import ValidationError

from src.llm.llm_schema import LLMExtractionResult


class DataValidator:
    def validate(self, data):
        try:
            validated = LLMExtractionResult.model_validate(data)

            normalized_data = validated.model_dump()

            return {
                "valid": True,
                "data": normalized_data,
                "errors": []
            }

        except ValidationError as error:
            return {
                "valid": False,
                "data": None,
                "errors": self._format_errors(error)
            }

    def _format_errors(self, error):
        errors = []

        for item in error.errors():
            location = ".".join(str(part) for part in item["loc"])

            errors.append({
                "field": location,
                "message": item["msg"],
                "type": item["type"]
            })

        return errors
```

<a id='file-src-database-database-py'></a>
### الملف: `src\database\database.py`
**المسار الكامل:** `E:\ZaWolf_project\src\database\database.py`

```python
import pyodbc


class Database:
    def __init__(self):
        self.connection_string = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=localhost;"
            "DATABASE=ZaWolfDB;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )

    def connect(self):
        return pyodbc.connect(self.connection_string)

    def execute(self, query, params=None):
        connection = self.connect()

        try:
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def insert_and_get_id(self, query, params=None):
        connection = self.connect()

        try:
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            connection.commit()
            return result[0]
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def fetch_one(self, query, params=None):
        connection = self.connect()

        try:
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchone()
        finally:
            connection.close()

    def test_connection(self):
        result = self.fetch_one("SELECT DB_NAME()")
        return result[0]
```

<a id='file-src-database-mapper-py'></a>
### الملف: `src\database\mapper.py`
**المسار الكامل:** `E:\ZaWolf_project\src\database\mapper.py`

```python
from src.database.database import Database
from src.database.repository import Repository
from src.database.relation_resolver import RelationResolver


class DatabaseMapper:
    def __init__(self):
        self.db = Database()
        self.resolver = RelationResolver()

        tables = [
            "locations",
            "staff",
            "clients",
            "medical_history",
            "vitals",
            "lab_results",
            "medications",
            "services",
            "appointments",
            "treatment_records",
            "consents",
            "photos",
            "invoices",
            "invoice_items",
            "payments",
            "packages",
            "client_packages",
            "products",
            "source_documents",
        ]

        self.repositories = {
            table: Repository(table)
            for table in tables
        }

    def save(self, data):
        connection = self.db.connect()
        cursor = connection.cursor()

        inserted = {
            table: []
            for table in self.repositories
        }

        try:
            self._insert_simple(
                "locations",
                data,
                cursor,
                inserted,
            )

            self._insert_staff(
                data,
                cursor,
                inserted,
            )

            client_ids = self._insert_clients(
                data,
                cursor,
                inserted,
            )

            self._insert_medical_data(
                data,
                client_ids,
                cursor,
                inserted,
            )

            self._insert_simple(
                "services",
                data,
                cursor,
                inserted,
            )

            self._insert_simple(
                "packages",
                data,
                cursor,
                inserted,
            )

            self._insert_simple(
                "products",
                data,
                cursor,
                inserted,
            )

            self._insert_appointments(
                data,
                cursor,
                inserted,
            )

            self._insert_treatments(
                data,
                cursor,
                inserted,
            )

            self._insert_consents(
                data,
                cursor,
                inserted,
            )

            self._insert_photos(
                data,
                cursor,
                inserted,
            )

            self._insert_invoices(
                data,
                cursor,
                inserted,
            )

            self._insert_invoice_items(
                data,
                cursor,
                inserted,
            )

            self._insert_payments(
                data,
                cursor,
                inserted,
            )

            self._insert_client_packages(
                data,
                client_ids,
                cursor,
                inserted,
            )

            self._insert_simple(
                "source_documents",
                data,
                cursor,
                inserted,
            )

            connection.commit()

            return inserted

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def _insert_simple(
        self,
        table,
        data,
        cursor,
        inserted,
    ):
        for record in data.get(table, []):
            record_id = self.repositories[table].insert(
                record,
                cursor,
            )

            inserted[table].append(record_id)

    def _insert_staff(
        self,
        data,
        cursor,
        inserted,
    ):
        for record in data.get("staff", []):
            record = record.copy()

            location_name = record.pop(
                "location_name",
                None,
            )

            if location_name:
                location_id = self.resolver.find_location(
                    location_name,
                    cursor,
                )

                if location_id is None:
                    raise ValueError(
                        f"Location not found: {location_name}"
                    )

                record["location_id"] = location_id

            record_id = self.repositories["staff"].insert(
                record,
                cursor,
            )

            inserted["staff"].append(record_id)

    def _insert_clients(
        self,
        data,
        cursor,
        inserted,
    ):
        client_ids = []

        for record in data.get("clients", []):
            record_id = self.repositories["clients"].insert(
                record,
                cursor,
            )

            client_ids.append(record_id)
            inserted["clients"].append(record_id)

        return client_ids

    def _insert_medical_data(
        self,
        data,
        client_ids,
        cursor,
        inserted,
    ):
        client_id = client_ids[0] if client_ids else None

        for table in [
            "medical_history",
            "vitals",
            "lab_results",
            "medications",
        ]:
            for record in data.get(table, []):
                if table != "medications" and client_id is None:
                    continue

                record = record.copy()

                if client_id is not None:
                    record["client_id"] = client_id

                record_id = self.repositories[table].insert(
                    record,
                    cursor,
                )

                inserted[table].append(record_id)

    def _insert_appointments(
        self,
        data,
        cursor,
        inserted,
    ):
        for record in data.get("appointments", []):
            record = record.copy()

            client_name = record.pop(
                "client_name",
                None,
            )

            staff_name = record.pop(
                "staff_name",
                None,
            )

            location_name = record.pop(
                "location_name",
                None,
            )

            service_name = record.pop(
                "service_name",
                None,
            )

            if client_name:
                if inserted["clients"]:
                    record["client_id"] = inserted["clients"][0]

                else:
                    parts = client_name.split(maxsplit=1)

                    client = {
                        "first_name": parts[0],
                        "last_name": (
                            parts[1]
                            if len(parts) > 1
                            else ""
                        ),
                        "mobile": None,
                    }

                    client_id = self.resolver.find_client(
                        client,
                        cursor,
                    )

                    if client_id is None:
                        raise ValueError(
                            f"Client not found: {client_name}"
                        )

                    record["client_id"] = client_id

            elif inserted["clients"]:
                record["client_id"] = inserted["clients"][0]

            if staff_name:
                staff_id = self.resolver.find_staff(
                    staff_name,
                    cursor,
                )

                if staff_id is None:
                    raise ValueError(
                        f"Staff not found: {staff_name}"
                    )

                record["staff_id"] = staff_id

            if location_name:
                location_id = self.resolver.find_location(
                    location_name,
                    cursor,
                )

                if location_id is None:
                    raise ValueError(
                        f"Location not found: {location_name}"
                    )

                record["location_id"] = location_id

            if service_name:
                service_id = self.resolver.find_service(
                    service_name,
                    cursor,
                )

                if service_id is None:
                    raise ValueError(
                        f"Service not found: {service_name}"
                    )

                record["service_id"] = service_id

            record_id = self.repositories[
                "appointments"
            ].insert(
                record,
                cursor,
            )

            inserted["appointments"].append(
                record_id
            )

    def _insert_treatments(
        self,
        data,
        cursor,
        inserted,
    ):
        for record in data.get(
            "treatment_records",
            [],
        ):
            record = record.copy()

            product_name = record.pop(
                "product_name",
                None,
            )

            if product_name:
                product_id = self.resolver.find_product(
                    product_name,
                    cursor,
                )

                if product_id is None:
                    raise ValueError(
                        f"Product not found: {product_name}"
                    )

                record["product_id"] = product_id

            if (
                "appointment_id" not in record
                and inserted["appointments"]
            ):
                record["appointment_id"] = (
                    inserted["appointments"][0]
                )

            record_id = self.repositories[
                "treatment_records"
            ].insert(
                record,
                cursor,
            )

            inserted["treatment_records"].append(
                record_id
            )

    def _insert_consents(
        self,
        data,
        cursor,
        inserted,
    ):
        for record in data.get(
            "consents",
            [],
        ):
            record = record.copy()

            record.pop(
                "appointment_id",
                None,
            )

            if inserted["clients"]:
                record["client_id"] = (
                    inserted["clients"][0]
                )

            record_id = self.repositories[
                "consents"
            ].insert(
                record,
                cursor,
            )

            inserted["consents"].append(
                record_id
            )

    def _insert_photos(
        self,
        data,
        cursor,
        inserted,
    ):
        for record in data.get(
            "photos",
            [],
        ):
            record = record.copy()

            record.pop(
                "treatment_id",
                None,
            )

            if inserted["clients"]:
                record["client_id"] = (
                    inserted["clients"][0]
                )

            if inserted["treatment_records"]:
                record["treatment_id"] = (
                    inserted["treatment_records"][0]
                )

            record_id = self.repositories[
                "photos"
            ].insert(
                record,
                cursor,
            )

            inserted["photos"].append(
                record_id
            )

    def _insert_invoices(
        self,
        data,
        cursor,
        inserted,
    ):
        for record in data.get(
            "invoices",
            [],
        ):
            record = record.copy()

            if inserted["clients"]:
                record["client_id"] = (
                    inserted["clients"][0]
                )

            if (
                "appointment_id" not in record
                and inserted["appointments"]
            ):
                record["appointment_id"] = (
                    inserted["appointments"][0]
                )

            record_id = self.repositories[
                "invoices"
            ].insert(
                record,
                cursor,
            )

            inserted["invoices"].append(
                record_id
            )

    def _insert_invoice_items(
        self,
        data,
        cursor,
        inserted,
    ):
        for record in data.get(
            "invoice_items",
            [],
        ):
            record = record.copy()

            if not inserted["invoices"]:
                raise ValueError(
                    "Cannot insert invoice item without invoice"
                )

            record.pop(
                "invoice_id",
                None,
            )

            record["invoice_id"] = (
                inserted["invoices"][0]
            )

            record_id = self.repositories[
                "invoice_items"
            ].insert(
                record,
                cursor,
            )

            inserted["invoice_items"].append(
                record_id
            )

    def _insert_payments(
        self,
        data,
        cursor,
        inserted,
    ):
        for record in data.get(
            "payments",
            [],
        ):
            record = record.copy()

            if not inserted["invoices"]:
                raise ValueError(
                    "Cannot insert payment without invoice"
                )

            record.pop(
                "invoice_id",
                None,
            )

            record["invoice_id"] = (
                inserted["invoices"][0]
            )

            record_id = self.repositories[
                "payments"
            ].insert(
                record,
                cursor,
            )

            inserted["payments"].append(
                record_id
            )

    def _insert_client_packages(
        self,
        data,
        client_ids,
        cursor,
        inserted,
    ):
        if not client_ids:
            return

        client_id = client_ids[0]

        for record in data.get(
            "client_packages",
            [],
        ):
            record = record.copy()

            package_name = record.pop(
                "package_name",
                None,
            )

            if not package_name:
                raise ValueError(
                    "client_package requires package_name"
                )

            package_id = self.resolver.find_package(
                package_name,
                cursor,
            )

            if package_id is None:
                raise ValueError(
                    f"Package not found: {package_name}"
                )

            record["client_id"] = client_id
            record["package_id"] = package_id

            record_id = self.repositories[
                "client_packages"
            ].insert(
                record,
                cursor,
            )

            inserted["client_packages"].append(
                record_id
            )
```

<a id='file-src-database-relation_resolver-py'></a>
### الملف: `src\database\relation_resolver.py`
**المسار الكامل:** `E:\ZaWolf_project\src\database\relation_resolver.py`

```python
from src.database.database import Database


class RelationResolver:
    def __init__(self):
        self.db = Database()

    def _fetch_one(self, query, params, cursor=None):
        if cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
        else:
            result = self.db.fetch_one(query, params)

        return result[0] if result else None

    def find_client(self, client, cursor=None):
        query = """
        SELECT TOP 1 id
        FROM clients
        WHERE first_name = ?
          AND last_name = ?
          AND (
              mobile = ?
              OR (? IS NULL AND mobile IS NULL)
          )
        """

        params = (
            client.get("first_name"),
            client.get("last_name"),
            client.get("mobile"),
            client.get("mobile"),
        )

        return self._fetch_one(query, params, cursor)

    def find_staff(self, full_name, cursor=None):
        return self._fetch_one(
            "SELECT TOP 1 id FROM staff WHERE full_name = ?",
            (full_name,),
            cursor,
        )

    def find_location(self, name, cursor=None):
        return self._fetch_one(
            "SELECT TOP 1 id FROM locations WHERE name = ?",
            (name,),
            cursor,
        )

    def find_service(self, name, cursor=None):
        return self._fetch_one(
            "SELECT TOP 1 id FROM services WHERE name = ?",
            (name,),
            cursor,
        )

    def find_product(self, name, cursor=None):
        return self._fetch_one(
            "SELECT TOP 1 id FROM products WHERE name = ?",
            (name,),
            cursor,
        )

    def find_package(self, name, cursor=None):
        return self._fetch_one(
            "SELECT TOP 1 id FROM packages WHERE name = ?",
            (name,),
            cursor,
        )
```

<a id='file-src-database-repository-py'></a>
### الملف: `src\database\repository.py`
**المسار الكامل:** `E:\ZaWolf_project\src\database\repository.py`

```python
from src.database.database import Database


class Repository:
    def __init__(self, table_name):
        self.db = Database()
        self.table_name = table_name

    def insert(self, data, cursor=None):
        columns = list(data.keys())
        values = list(data.values())

        column_names = ", ".join(columns)
        placeholders = ", ".join("?" for _ in values)

        query = f"""
        INSERT INTO {self.table_name} ({column_names})
        OUTPUT INSERTED.id
        VALUES ({placeholders})
        """

        if cursor:
            cursor.execute(query, values)
            return cursor.fetchone()[0]

        return self.db.insert_and_get_id(query, values)

    def get_by_id(self, record_id):
        query = f"""
        SELECT *
        FROM {self.table_name}
        WHERE id = ?
        """

        return self.db.fetch_one(query, (record_id,))
```

<a id='file-src-database-client_repository-py'></a>
### الملف: `src\database\client_repository.py`
**المسار الكامل:** `E:\ZaWolf_project\src\database\client_repository.py`

```python
from src.database.database import Database


class ClientRepository:
    def __init__(self):
        self.db = Database()

    def create(self, client):
        query = """
        INSERT INTO clients (
            first_name,
            last_name,
            dob,
            gender,
            mobile,
            email,
            address,
            lead_source,
            medical_alerts,
            opt_in_sms
        )
        OUTPUT INSERTED.id
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            client.get("first_name"),
            client.get("last_name"),
            client.get("dob"),
            client.get("gender"),
            client.get("mobile"),
            client.get("email"),
            client.get("address"),
            client.get("lead_source"),
            client.get("medical_alerts"),
            client.get("opt_in_sms"),
        )

        result = self.db.fetch_one(query, params)
        return result[0]
```

<a id='file-src-database-appointment_repository-py'></a>
### الملف: `src\database\appointment_repository.py`
**المسار الكامل:** `E:\ZaWolf_project\src\database\appointment_repository.py`

```python
from src.database.database import Database


class AppointmentRepository:
    def __init__(self):
        self.db = Database()

    def create(
        self,
        client_id,
        staff_id,
        location_id,
        service_id,
        room=None,
        start_at=None,
        end_at=None,
        status=None,
        notes=None,
    ):
        query = """
        INSERT INTO appointments (
            client_id,
            staff_id,
            location_id,
            service_id,
            room,
            start_at,
            end_at,
            status,
            notes
        )
        OUTPUT INSERTED.id
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            client_id,
            staff_id,
            location_id,
            service_id,
            room,
            start_at,
            end_at,
            status,
            notes,
        )

        return self.db.insert_and_get_id(query, params)
```

<a id='file-src-database-consent_repository-py'></a>
### الملف: `src\database\consent_repository.py`
**المسار الكامل:** `E:\ZaWolf_project\src\database\consent_repository.py`

```python
from src.database.database import Database


class ConsentRepository:
    def __init__(self):
        self.db = Database()

    def create(
        self,
        client_id,
        appointment_id=None,
        consent_type=None,
        signed_at=None,
        file_ref=None,
    ):
        query = """
        INSERT INTO consents (
            client_id,
            appointment_id,
            consent_type,
            signed_at,
            file_ref
        )
        OUTPUT INSERTED.id
        VALUES (?, ?, ?, ?, ?)
        """

        params = (
            client_id,
            appointment_id,
            consent_type,
            signed_at,
            file_ref,
        )

        return self.db.insert_and_get_id(query, params)
```

<a id='file-src-database-invoice_repository-py'></a>
### الملف: `src\database\invoice_repository.py`
**المسار الكامل:** `E:\ZaWolf_project\src\database\invoice_repository.py`

```python
from src.database.database import Database


class InvoiceRepository:
    def __init__(self):
        self.db = Database()

    def create(
        self,
        client_id,
        appointment_id=None,
        issue_date=None,
        subtotal=None,
        discount=None,
        tax=None,
        total=None,
        status=None,
    ):
        query = """
        INSERT INTO invoices (
            client_id,
            appointment_id,
            issue_date,
            subtotal,
            discount,
            tax,
            total,
            status
        )
        OUTPUT INSERTED.id
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            client_id,
            appointment_id,
            issue_date,
            subtotal,
            discount,
            tax,
            total,
            status,
        )

        return self.db.insert_and_get_id(query, params)
```

<a id='file-src-database-invoice_item_repository-py'></a>
### الملف: `src\database\invoice_item_repository.py`
**المسار الكامل:** `E:\ZaWolf_project\src\database\invoice_item_repository.py`

```python
from src.database.database import Database


class InvoiceItemRepository:
    def __init__(self):
        self.db = Database()

    def create(
        self,
        invoice_id,
        item_type=None,
        item_id=None,
        description=None,
        qty=None,
        unit_price=None,
        line_total=None,
    ):
        query = """
        INSERT INTO invoice_items (
            invoice_id,
            item_type,
            item_id,
            description,
            qty,
            unit_price,
            line_total
        )
        OUTPUT INSERTED.id
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            invoice_id,
            item_type,
            item_id,
            description,
            qty,
            unit_price,
            line_total,
        )

        return self.db.insert_and_get_id(query, params)
```

<a id='file-src-database-package_repository-py'></a>
### الملف: `src\database\package_repository.py`
**المسار الكامل:** `E:\ZaWolf_project\src\database\package_repository.py`

```python
from src.database.database import Database


class PackageRepository:
    def __init__(self):
        self.db = Database()

    def create(
        self,
        name,
        sessions_count=None,
        price=None,
        validity_days=None,
    ):
        query = """
        INSERT INTO packages (
            name,
            sessions_count,
            price,
            validity_days
        )
        OUTPUT INSERTED.id
        VALUES (?, ?, ?, ?)
        """

        params = (
            name,
            sessions_count,
            price,
            validity_days,
        )

        return self.db.insert_and_get_id(query, params)
```

<a id='file-src-database-client_package_repository-py'></a>
### الملف: `src\database\client_package_repository.py`
**المسار الكامل:** `E:\ZaWolf_project\src\database\client_package_repository.py`

```python
from src.database.database import Database


class ClientPackageRepository:
    def __init__(self):
        self.db = Database()

    def create(
        self,
        client_id,
        package_id,
        remaining_sessions=None,
        expires_at=None,
    ):
        query = """
        INSERT INTO client_packages (
            client_id,
            package_id,
            remaining_sessions,
            expires_at
        )
        OUTPUT INSERTED.id
        VALUES (?, ?, ?, ?)
        """

        params = (
            client_id,
            package_id,
            remaining_sessions,
            expires_at,
        )

        return self.db.insert_and_get_id(query, params)
```

<a id='file-src-database-payment_repository-py'></a>
### الملف: `src\database\payment_repository.py`
**المسار الكامل:** `E:\ZaWolf_project\src\database\payment_repository.py`

```python
from src.database.database import Database


class PaymentRepository:
    def __init__(self):
        self.db = Database()

    def create(
        self,
        invoice_id,
        amount,
        method=None,
        paid_at=None,
        reference=None,
    ):
        query = """
        INSERT INTO payments (
            invoice_id,
            amount,
            method,
            paid_at,
            reference
        )
        OUTPUT INSERTED.id
        VALUES (?, ?, ?, ?, ?)
        """

        params = (
            invoice_id,
            amount,
            method,
            paid_at,
            reference,
        )

        return self.db.insert_and_get_id(query, params)
```

<a id='file-src-database-photo_repository-py'></a>
### الملف: `src\database\photo_repository.py`
**المسار الكامل:** `E:\ZaWolf_project\src\database\photo_repository.py`

```python
from src.database.database import Database


class PhotoRepository:
    def __init__(self):
        self.db = Database()

    def create(
        self,
        client_id,
        treatment_id=None,
        photo_type=None,
        taken_at=None,
        file_ref=None,
    ):
        query = """
        INSERT INTO photos (
            client_id,
            treatment_id,
            type,
            taken_at,
            file_ref
        )
        OUTPUT INSERTED.id
        VALUES (?, ?, ?, ?, ?)
        """

        params = (
            client_id,
            treatment_id,
            photo_type,
            taken_at,
            file_ref,
        )

        return self.db.insert_and_get_id(query, params)
```

<a id='file-src-database-source_document_repository-py'></a>
### الملف: `src\database\source_document_repository.py`
**المسار الكامل:** `E:\ZaWolf_project\src\database\source_document_repository.py`

```python
from src.database.database import Database


class SourceDocumentRepository:
    def __init__(self):
        self.db = Database()

    def create(
        self,
        file_name,
        doc_type=None,
        ocr_text=None,
        llm_json=None,
        confidence=None,
        review_status=None,
    ):
        query = """
        INSERT INTO source_documents (
            file_name,
            doc_type,
            ocr_text,
            llm_json,
            confidence,
            review_status
        )
        OUTPUT INSERTED.id
        VALUES (?, ?, ?, ?, ?, ?)
        """

        params = (
            file_name,
            doc_type,
            ocr_text,
            llm_json,
            confidence,
            review_status,
        )

        return self.db.insert_and_get_id(query, params)
```

<a id='file-src-database-treatment_repository-py'></a>
### الملف: `src\database\treatment_repository.py`
**المسار الكامل:** `E:\ZaWolf_project\src\database\treatment_repository.py`

```python
from src.database.database import Database


class TreatmentRepository:
    def __init__(self):
        self.db = Database()

    def create(
        self,
        appointment_id,
        product_id,
        units=None,
        lot_number=None,
        expiry_date=None,
        area=None,
        injection_sites=None,
        depth=None,
        device_settings=None,
        skin_response=None,
        aftercare=None,
    ):
        query = """
        INSERT INTO treatment_records (
            appointment_id,
            product_id,
            units,
            lot_number,
            expiry_date,
            area,
            injection_sites,
            depth,
            device_settings,
            skin_response,
            aftercare
        )
        OUTPUT INSERTED.id
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            appointment_id,
            product_id,
            units,
            lot_number,
            expiry_date,
            area,
            injection_sites,
            depth,
            device_settings,
            skin_response,
            aftercare,
        )

        return self.db.insert_and_get_id(query, params)
```
