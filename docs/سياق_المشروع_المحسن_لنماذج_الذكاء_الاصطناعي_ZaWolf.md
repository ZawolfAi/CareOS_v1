# مواصفات وسياق نظام ZaWolf المهيأ لنماذج الذكاء الاصطناعي (AI System Context Specification)
# توجيه المعالجة: اقرأ واحتفظ في الذاكرة العاملة (Working Memory) — هذا الملف يمثل المرجع المعماري الصارم للنموذج.

```yaml
system_identity:
  name: ZaWolf_project
  type: Enterprise Medical Document Intelligence, Multimodal Vision OCR, and Relational SQL Server Persistence
  version: 1.0.0 (Production Final Release)
  deployment_model: Local / On-Premise Only (Air-gapped compatible, Zero External Cloud API Dependency)
  runtime_environment:
    os: Windows
    python_version: 3.11.9
    dbms: Microsoft SQL Server 2022 (Local, Windows Auth / Trusted_Connection)
    llm_runtime: Ollama Local Server (http://localhost:11434, default model: qwen3:latest)
    vision_ocr_backend: PaddleOCR (Arabic/English printed) + HuggingFace Transformers (Qwen2.5-VL-3B for handwriting)
    api_gateway: FastAPI + Uvicorn (RESTful Endpoints + Interactive Swagger UI)
    threading_model: Hardware-Adaptive Physical Core Detection via psutil
  project_root: "E:\\ZaWolf_project"
  timestamp_updated: "2026-10-01"
```

---

## 1. القواعد الهندسية الثابتة للنظام (Core System Invariants)

أي نموذج ذكاء اصطناعي يتعامل مع هذا الكود البرمجي يجب ألا يكسر هذه القواعد الجوهرية:

1. **كشف وتوجيه قطعي للملفات (Deterministic Routing):** تحديد نوع الملف يعتمد حصرياً على امتداد الملف في `src/ingestion/file_detector.py` ويتم توجيهه ميكانيكياً في `src/ingestion/router.py`. ممنوع التخمين أو التوجيه الاحتمالي.
2. **المسار الموحد للصور والـ OCR الممسوح:** مستندات PDF الممسوحة ضوئياً (Scanned PDF) لا تمتلك محرك OCR منفصل؛ بل تتحول صفحاتها لصور عبر PyMuPDF وتدخل نفس مسار الصور والـ OCR الموحد.
3. **منع الـ OCR على البيانات المنظمة ومستندات Word:** مستندات Word وجداول Excel و CSV لا تمر على OCR نهائياً؛ تستخرج الجداول متجهة عبر Pandas DataFrames في أقل من 0.1 ثانية، وتستخرج مستندات Word عبر DOM لـ python-docx.
4. **التكيف التلقائي مع عتاد المعالج (Hardware-Adaptive Threading):** كشف عدد الأنوية الفيزيائية تلقائياً وتمريرها لـ Ollama لمنع الاختناق وتوفير قابلية النقل لأي سيرفر دون تعديل كود.
5. **الإغلاق الإجباري للمقابس والجلسات (Managed Sockets):** تجميع الاتصالات في `requests.Session` مع مهلة 90 ثانية، واستدعاء إلزامي لـ `close()` في كتلة `finally:` لتفريغ المقابس ومنع تسريب الذاكرة.
6. **فهارس تغطوية لقاعدة البيانات (Covering Indexes):** الاعتماد على 13 فهرساً تغطوياً في SQL Server لتسريع عمليات الربط ومنع الـ Full Table Scans.
7. **منع الهلوسة وعزل الروشتات (ExtractionGuard):** إذا كشف حارس الاستخراج أن الملف روشتة علاجية، يتم فوراً تصفير كافة الجداول غير المتعلقة بالأدوية لمنع الهلوسة.
8. **المعاملات الذرية لقاعدة البيانات (Atomic Persistence):** يتم حفظ كافة كيانات المستند عبر معاملة ذرية واحدة داخل `src/database/mapper.py`، وفي حال حدوث أي خطأ يتم التراجع التام فوراً (`rollback`).

---

## 2. مخطط تدفق البيانات الكامل (Data Flow Architecture)

```
[Inbound Medical File]
       │
       ▼
[src/ingestion/file_detector.py :: detect_file_type()]
       │
       ▼
[src/ingestion/router.py :: route_file()]
       ├─────────────────┬────────────────────┬─────────────────┬─────────────────┐
       │ (pdf)           │ (image)            │ (word)          │ (excel / csv)   │
       ▼                 ▼                    ▼                 ▼                 │
[pdf_pipeline]    [image_pipeline]     [word_pipeline]   [structured]             │ (unsupported)
       │                 │                    │                 │                 ▼
       ├─ Digital        │                    ├─ Word Chunks    │             [Status:
       │   │             │                    │  (Sliding Win)  │            unsupported]
       │   ▼             │                    │                 │
       │ [fitz extract]  │                    │                 │
       │   │             │                    │                 │
       │   ▼             │                    │                 │
       │ [Batch Chunks]  │                    │                 │
       │                 │                    │                 │
       └─ Scanned        │                    │                 │
           │             │                    │                 │
           ▼             │                    │                 │
     [fitz render]       │                    │                 │
     (pages -> images)   │                    │                 │
           │             │                    │                 │
           └──────┬──────┘                    │                 │
                  │                           │                 │
                  ▼                           │                 │
     [src/processors/image_processor.py]      │                 │
     (EXIF transpose, Grayscale, Contrast)    │                 │
                  │                           │                 │
                  ▼                           │                 │
     [src/ocr/ocr_router.py :: OCRRouter]     │                 │
     ├── engine="auto"                        │                 │
     │   ├── Printed Text -> PaddleOCR (<1s)  │                 │
     │   └── Handwriting  -> Qwen2.5-VL-3B    │                 │
                  │                           │                 │
                  ▼                           │                 │
         [Extracted Raw Text]                 │                 │
                  │                           │                 │
                  └─────────────┬─────────────┘                 │
                                │                               │
                                ▼                               │
     [src/llm/llm_processor.py :: LLMProcessor]                 │
     ├── Context-Compressed System Prompt                       │
     ├── Ollama REST API (Qwen3-8B) with Physical Cores         │
     └── JSON Extraction Contract                               │
                                │                               │
                                ▼                               │
     [src/validation/extraction_guard.py]                       │
     (Zero-out hallucinated entities in prescriptions)          │
                                │                               │
                                ▼                               │
     [src/validation/validator.py :: DataValidator]             │
     (Pydantic v2 Schema Conformity)                            │
                                │                               │
                                ▼                               │
     [src/database/relation_resolver.py]                        │
     (Resolve Foreign Keys: clients, locations, staff)          │
                                │                               │
                                ▼                               │
     [src/database/mapper.py :: DatabaseMapper]                 │
     (Single-Transaction Atomic Unit of Work across 19 tables)  │
                                │                               │
                                ├───────────────────────────────┘
                                ▼
         [Microsoft SQL Server: ZaWolfDB]
         ├── 19 Relational Normalized Tables
         └── 13 Non-Clustered Covering Indexes
                                │
                                ▼
         [FastAPI REST API Gateway /run_api.py]
         ├── POST /api/v1/process
         ├── GET  /api/v1/health
         ├── GET  /api/v1/metrics
         └── Interactive Swagger Docs at /docs
```

---

## 3. مواصفات الجداول الـ 19 في قاعدة البيانات (Relational Entity Catalog)

1. `locations` (المستشفيات، المراكز، الفروع)
2. `staff` (الأطباء، الممرضون، الفنيون)
3. `clients` (المرضى، الهوية، الهاتف)
4. `medical_history` (الأمراض المزمنة، الحساسيات)
5. `vitals` (الضغط، النبض، الحرارة، السكر)
6. `lab_results` (التحاليل المعملية، القيم المرجعية)
7. `medications` (الأدوية، الجرعات، التكرار)
8. `services` (الخدمات الطبية، الكشوفات)
9. `appointments` (المواعيد، التاريخ، الحالة)
10. `treatment_records` (سجلات العلاج، الملاحظات)
11. `consents` (الإقرارات الطبية والموافقات)
12. `photos` (الصور الطبية والأشعة)
13. `invoices` (الفواتير، الإجمالي، التاريخ)
14. `invoice_items` (بنود الفواتير)
15. `payments` (المدفوعات وطرق السداد)
16. `packages` (الباقات العلاجية)
17. `client_packages` (اشتراكات المرضى بالباقات)
18. `products` (المستلزمات الصيدلانية)
19. `source_documents` (أصل المستندات، مسار الاستخراج، الـ OCR والـ LLM JSON)

---

## 4. الفهارس التغطوية الـ 13 (Covering Indexes)

تم بناء الفهارس التالية داخل `ZaWolfDB` لتوفير سرعة استعلام فائقة (Lookup < 1ms):
* `IX_appointments_client_id` (مع تضمين `appointment_date`, `status`)
* `IX_client_packages_client_id`
* `IX_consents_client_id`
* `IX_invoice_items_invoice_id`
* `IX_invoices_client_id`
* `IX_lab_results_client_id` (مع تضمين `test_name`, `test_value`)
* `IX_medical_history_client_id`
* `IX_medications_client_id` (مع تضمين `medication_name`, `dosage`)
* `IX_payments_invoice_id`
* `IX_photos_client_id`
* `IX_source_documents_doc_type`
* `IX_treatment_records_client_id`
* `IX_vitals_client_id` (مع تضمين `recorded_at`)

---

## 5. مواصفات الأداء الميداني والتقييم (Benchmark Results)

* أداة الفحص: [`evaluate_input_files.py`](file:///E:/ZaWolf_project/evaluate_input_files.py)
* معدل النجاح: **100.0% PASS** عبر كافة أنواع المدخلات (8 / 8 ملفات).
* المعالجة المتجهة لجداول CSV: **0.08 ثانية**.
* زمن قراءة الصور المطبوعة: **40 - 65 ثانية**.
* دقة استخراج الروشتة اليدوية: **4 أدوية سريرية مستخرجة** ومسكنة بالـ Foreign Keys بنجاح تام.
