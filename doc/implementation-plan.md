# Phase-Wise Implementation Plan: Mutual Fund FAQ Assistant (Facts-Only RAG)

---

## Project Overview

This implementation plan outlines the phased roadmap for building the **Mutual Fund FAQ Assistant**, an ultra-reliable, facts-only RAG application adhering strictly to the specifications defined in [`doc/problemStatement.md`](file:///Users/jeevanshu/Documents/Investment%20Assistant/Investment-Assistant/doc/problemStatement.md) and [`doc/Architecture.md`](file:///Users/jeevanshu/Documents/Investment%20Assistant/Investment-Assistant/doc/Architecture.md).

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CORE DESIGN PRINCIPLES                          │
│  1. Accuracy Over Intelligence (Zero hallucination / zero advice)      │
│  2. Strict Response Format (≤ 3 sentences, 1 URL, timestamp footer)    │
│  3. Zero PII Storage or Processing (Immediate regex block & sanitize)  │
│  4. Whitelisted Groww Scheme Citations Only (groww.in/mutual-funds)    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Phase Breakdown & Milestone Roadmap

```mermaid
gantt
    title Project Implementation Roadmap
    dateFormat  X
    axisFormat Phase %d
    section Setup & Foundation
    Phase 1: Environment & Project Scaffolding    :active, p1, 0, 1
    Phase 2: Corpus Curation & Ingestion Pipeline :p2, after p1, 1d
    section Core RAG & Compliance
    Phase 3: Vector Embeddings & Retrieval Engine :p3, after p2, 1d
    Phase 4: Guardrails, Routing & Refusal Engine :p4, after p3, 1d
    Phase 5: Constrained LLM Generation & Output Validator :p5, after p4, 1d
    section API & UI Experience
    Phase 6: Backend API Layer (FastAPI)         :p6, after p5, 1d
    Phase 7: Daily Ingestion Scheduler (GitHub Actions) :p7, after p6, 1d
    section Verification & Release
    Phase 8: Test Suite, Compliance Evaluation & Docs :p8, after p7, 1d
```

---

## Phase 1: Environment Setup & Project Scaffolding

### Objective
Establish the repository directory structure, Python virtual environment, dependencies, and configuration management.

### Key Tasks
1. **Directory Structure Setup**:
   ```
   Investment-Assistant/
   ├── backend/
   │   ├── app/
   │   │   ├── api/          # Route handlers (chat, health, schemes)
   │   │   ├── core/         # Config, logging, settings
   │   │   ├── guardrails/   # PII filter, advisory classifier, format validator
   │   │   ├── rag/          # Ingestion, embeddings, retriever, generator
   │   │   └── schemas/      # Pydantic request/response models
   │   ├── tests/            # Pytest test suite
   │   └── main.py           # FastAPI entrypoint
   ├── data/
   │   ├── raw/              # Extracted Groww scheme page content & schemas
   │   ├── processed/        # Structured JSON scheme parameters
   │   └── vector_store/     # Persistent ChromaDB index
   ├── frontend/
   │   ├── index.html        # Clean, responsive single-page chat UI
   │   ├── styles.css        # Groww-inspired theme & animations
   │   └── app.js            # Client-side chat logic & prompt chips
   ├── doc/                  # Centralized documentation
   ├── requirements.txt      # Python dependencies
   ├── .env.example          # Environment variables template
   └── README.md             # Project overview & setup instructions
   ```
2. **Dependency Configuration (`requirements.txt`)**:
   - `fastapi`, `uvicorn[standard]`, `pydantic`, `pydantic-settings`
   - `chromadb` / `faiss-cpu`, `sentence-transformers`
   - `groq` (Groq official Python SDK for ultra-fast LPU inference)
   - `pytest`, `pytest-asyncio`, `python-dotenv`, `httpx`
3. **Environment & Settings Setup**:
   - Create `.env.example` with config keys (`GROQ_API_KEY`, `GROQ_MODEL`, `PORT`, `ALLOW_ORIGINS`, `DATA_SOURCE_PATH`).
   - Implement `backend/app/core/config.py` using Pydantic Settings.

### Deliverables & Acceptance Criteria
- [ ] Clean directory tree created.
- [ ] Dependencies documented in `requirements.txt`.
- [ ] Config loader functioning with default fallbacks.

---

## Phase 2: Corpus Curation & Data Ingestion Pipeline

### Objective
Extract, structure, and validate official factual data for the 5 selected HDFC Mutual Fund schemes.

### Target Schemes
| # | Scheme Name | Category | Primary Reference URL |
| :-: | :--- | :--- | :--- |
| 1 | **HDFC Mid-Cap Opportunities Fund** | Equity: Mid Cap | `https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth` |
| 2 | **HDFC Small Cap Fund** | Equity: Small Cap | `https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth` |
| 3 | **HDFC Gold ETF Fund of Fund** | Commodities: FoF | `https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth` |
| 4 | **HDFC Top 100 / Large Cap Fund** | Equity: Large Cap | `https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth` |
| 5 | **HDFC ELSS Tax Saver Fund** | Equity: ELSS | `https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth` |

### Key Tasks
1. **Factual Schema Definition (Completed)**:
   - Structured and normalized dataset in [`data/processed/schemes.json`](file:///Users/jeevanshu/Documents/Investment%20Assistant/Investment-Assistant/data/processed/schemes.json) capturing verified attributes for each scheme:
     - Expense Ratio (Direct vs. Regular TER)
     - Exit Load rules & duration thresholds (e.g. 1% <= 1 year / Nil)
     - Minimum SIP and Lump Sum limits (₹100 / ₹500)
     - Lock-in period (3 years for ELSS, Nil for open-ended)
     - Riskometer rating (Very High, High)
     - Benchmark index (NIFTY Midcap 150 TRI, BSE 250 SmallCap TRI, Gold Price, NIFTY 100 TRI, NIFTY 500 TRI)
     - Statement & Capital Gains download procedure
     - Whitelisted official source citation URL & Last updated date

2. **Atomic Parameter-Domain Chunking Strategy (`backend/app/rag/chunker.py`)**:
   Rather than arbitrary character/token splitting, the corpus is partitioned into **atomic parameter-domain chunks** directly mapped from [`data/processed/schemes.json`](file:///Users/jeevanshu/Documents/Investment%20Assistant/Investment-Assistant/data/processed/schemes.json):
   - **Scheme Chunks (7 parameter domains × 5 schemes = 35 chunks)**:
     1. `fund_overview`: Scheme Name, Category, Plan Type, AMC, Fund Objective, Benchmark Index, and Riskometer.
     2. `expense_ratio`: Direct Plan TER %, Regular Plan TER %, and fee narrative.
     3. `exit_load`: Holding period thresholds (365 days / 15 days / Nil), fee percentages, and switch-out rules.
     4. `investment_limits`: Minimum SIP installment (₹100 / ₹500), initial lump sum, additional purchase limits, and frequency.
     5. `lock_in_period`: Statutory lock-in status, duration (3 years for ELSS / Nil for open-ended), and redemption restrictions.
     6. `taxation`: Equity vs. non-equity taxation, STCG (20%), LTCG (12.5% > ₹1.25L), Section 80C deductions.
     7. `operations`: Scheme-specific statement download procedure and folio verification.
   - **General Operations Chunks (3 chunks)**:
     8. `statement_download_general`: General Groww / AMC statement download workflow.
     9. `capital_gains_report_general`: Capital gains Schedule 112A report download workflow for ITR filing.
     10. `educational_resources_general`: Whitelisted links for Groww Mutual Funds Hub, AMFI, and SEBI portals.
   - **Total Processed Corpus Chunks**: Exactly **38 structured atomic chunks**.

3. **Structured Chunk Metadata Contract (`backend/app/schemas/chunk.py`)**:
   Every generated chunk strictly adheres to the following metadata structure:
   ```json
   {
     "chunk_id": "hdfc_mid_cap_fund_direct_growth_exit_load",
     "scheme_code": "hdfc-mid-cap-fund-direct-growth",
     "scheme_name": "HDFC Mid-Cap Opportunities Fund",
     "category": "Equity: Mid Cap",
     "parameter": "exit_load",
     "title": "HDFC Mid-Cap Opportunities Fund - Exit Load & Holding Duration",
     "content": "For units redeemed or switched out within 1 year (365 days) from the date of allotment, an exit load of 1.00% is applicable. No exit load is payable for units redeemed after 1 year.",
     "official_source_url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
     "last_updated": "2024-04-01",
     "keywords": ["exit load", "redemption charge", "holding period", "1 year", "1%", "hdfc mid cap"]
   }
   ```

4. **Data Integrity Validator (`backend/app/rag/validator.py`)**:
   - Validate 100% of chunks against the Pydantic `KnowledgeChunk` schema.
   - Verify every chunk has a non-empty `content` string with concise length.
   - Enforce that `official_source_url` strictly begins with `https://groww.in/`.
   - Verify `last_updated` matches `YYYY-MM-DD`.

### Deliverables & Acceptance Criteria
- [x] Complete [`data/processed/schemes.json`](file:///Users/jeevanshu/Documents/Investment%20Assistant/Investment-Assistant/data/processed/schemes.json) dataset for all 5 schemes.
- [x] Chunking engine [`backend/app/rag/chunker.py`](file:///Users/jeevanshu/Documents/Investment%20Assistant/Investment-Assistant/backend/app/rag/chunker.py) generating 38 structured chunks in [`data/processed/chunks.json`](file:///Users/jeevanshu/Documents/Investment%20Assistant/Investment-Assistant/data/processed/chunks.json).
- [x] Chunk validator [`backend/app/rag/validator.py`](file:///Users/jeevanshu/Documents/Investment%20Assistant/Investment-Assistant/backend/app/rag/validator.py) passing with zero integrity errors.
- [x] Zero missing parameter fields across all schemes.

---

## Phase 3: Vector Embeddings & Optimal Retrieval Engine

### Objective
Implement a high-precision, two-stage scheme-filtered hybrid retrieval engine that eliminates cross-scheme collisions and guarantees deterministic factual retrieval.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   TWO-STAGE FILTERED RETRIEVAL PIPELINE                │
│                                                                        │
│  User Query ──► [Stage 1: Entity & Parameter Resolver]                │
│                         │                                              │
│                         ├─► Scheme Resolved? (e.g. 'hdfc-mid-cap')     │
│                         ├─► Parameter Intent? (e.g. 'exit_load')       │
│                         └─► Ambiguous/Missing? (Route Disambiguation)  │
│                                                                        │
│                         ▼                                              │
│                 [Stage 2: ChromaDB Metadata-Filtered Search]           │
│                   - Dense Embedding (all-MiniLM-L6-v2)                 │
│                   - Hard Filter: where={"scheme_code": resolved}       │
│                   - Parameter Match Re-ranking Boost                   │
│                   - Top-1 (or Top-2) Retrieval Context                 │
│                                                                        │
│                         ▼                                              │
│                 [Grounded Retrieval Payload Delivery]                  │
│                   {content, official_source_url, last_updated}         │
└────────────────────────────────────────────────────────────────────────┘
```

### Retrieval Analysis & Best Strategy Design
Given the curated 38-chunk atomic corpus, pure unstructured semantic search suffers from **cross-scheme parameter bleeding** (e.g., retrieving ELSS 3-year lock-in for a Mid-Cap fund query). To achieve 100% precision, the optimal strategy combines:

1. **Stage 1: Query Entity Resolution & Intent Classification (`backend/app/rag/entity_resolver.py`)**:
   - **Scheme Alias Resolution**: Fast regex/token matching against `sources_manifest.json` aliases (e.g., *"midcap"*, *"hdfc tax saver"*, *"gold fof"*, *"large cap"*).
   - **Parameter Intent Detection**: Keyword/regex heuristics identifying target parameter domain (`expense_ratio`, `exit_load`, `investment_limits`, `lock_in_period`, `taxation`, `operations`, `statements`).
   - **Ambiguity Interception**: If user asks a parameter question without mentioning any fund (e.g., *"What is the minimum SIP?"*), flag `AMBIGUOUS_SCHEME` to prompt scheme selection rather than returning an arbitrary fund chunk.

2. **Stage 2: Scheme-Filtered Dense Semantic Vector Indexing (`backend/app/rag/vector_store.py`)**:
   - **Embedded Store**: Persistent ChromaDB (`data/vector_store/`) index.
   - **Dense Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors, sub-5ms latency, local CPU inference with zero network overhead).
   - **Hard Metadata Filtering**: When scheme is resolved, execute vector query with `where={"scheme_code": resolved_scheme_code}`.
   - **Parameter Boosting**: If parameter intent is identified, re-rank and prioritize chunks where `parameter == resolved_parameter`.

3. **Stage 3: Filtered Retriever Engine (`backend/app/rag/retriever.py`)**:
   - Primary retrieval count: $k=1$ (or $k=2$ for combined overview + operational queries).
   - Confidence threshold: Cosine similarity score $\ge 0.65$.
   - Payload assembly: Returns chunk text, parameter type, verified Groww canonical URL, and last updated date.

### Key Tasks
1. **Vector Store Service (`backend/app/rag/vector_store.py`)**:
   - Build ChromaDB vector collection manager with automatic initialization and chunk ingestion from `data/processed/chunks.json`.
   - Persist embeddings locally under `data/vector_store/`.
2. **Entity & Parameter Resolver (`backend/app/rag/entity_resolver.py`)**:
   - Match raw query strings to canonical scheme codes, general operations, or ambiguous states.
3. **Hybrid Filtered Retriever (`backend/app/rag/retriever.py`)**:
   - Combine entity resolution with ChromaDB metadata filtering and similarity search.
4. **Retrieval Verification Suite (`backend/tests/test_retriever.py`)**:
   - Benchmark precision across all 30 core factual queries in the golden evaluation dataset.

### Deliverables & Acceptance Criteria
- [x] ChromaDB persistent vector index initialized in `data/vector_store/`.
- [x] `EntityResolver` accurately resolving 100% of scheme aliases and parameter intents.
- [x] 0% cross-scheme retrieval collision rate (verified via automated tests).
- [x] Top-1 retrieval latency $< 20\text{ms}$ on CPU.

---

## Phase 4: Guardrails, Routing & Refusal Engine

### Objective
Implement pre-retrieval safety filters to detect PII, intercept advisory/speculative queries, and handle return calculation requests.

### Key Tasks
1. **PII Detector & Sanitizer (`backend/app/guardrails/pii_filter.py`)**:
   - Regex patterns for Indian financial PII:
     - PAN: `[A-Z]{5}[0-9]{4}[A-Z]`
     - Aadhaar: `\b\d{4}\s?\d{4}\s?\d{4}\b`
     - Phone: `\b(?:\+91|0)?[6-9]\d{9}\b`
     - OTPs: `\b\d{4,6}\b` in OTP context
     - Email: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`
   - Immediately abort processing on PII match and return security refusal without logging raw input.
2. **Intent Classifier & Policy Router (`backend/app/guardrails/intent_router.py`)**:
   - Classify queries into:
     - `FACTUAL`: Proceed to retrieval.
     - `ADVISORY`: "Should I invest?", "Which fund is best?", "Predict future price".
     - `COMPARISON`: "Is Fund A better than Fund B?".
     - `PERFORMANCE_CALC`: "Calculate 10k in 5 years", "What returns will I get?".
3. **Refusal Handler (`backend/app/guardrails/refusal_handler.py`)**:
   - Generate polite, compliant refusals reinforcing the facts-only scope.
   - Attach verified Groww educational / guidelines links:
     - General Advisory Refusal: `https://groww.in/mutual-funds`
     - Performance Queries: Provide direct link to the corresponding Groww scheme page URL (`groww.in/mutual-funds/...`).

### Deliverables & Acceptance Criteria
- [x] 100% of PII patterns intercepted before LLM or retrieval invocation.
- [x] Advisory and comparative questions reliably routed to the refusal handler.

---

## Phase 5: Constrained LLM Generation, Rate Limiter & Output Validator

### Objective
Implement the constrained generation prompt, client-side rate/token quota limiter for `openai/gpt-oss-120b`, and a deterministic post-generation validator guaranteeing strict format compliance and 100% service uptime.

### Key Tasks
1. **LPU Rate & Token Quota Limiter (`backend/app/rag/rate_limiter.py`)**:
   - Strictly enforces Groq Free Tier limits on `openai/gpt-oss-120b`:
     - **Requests per Minute (RPM)**: 30
     - **Requests per Day (RPD)**: 1,000
     - **Tokens per Minute (TPM)**: 8,000 (~8K)
     - **Tokens per Day (TPD)**: 200,000 (~200K)
   - Sliding 60-second window and daily counters track live consumption.
   - **Proactive Fallback**: When any quota threshold is reached or when Groq returns HTTP 429 (`RateLimitError`), the system proactively diverts execution to the zero-latency deterministic fallback engine (`_fallback_synthesis`), ensuring zero user disruption and zero API error leakage.
   - Sets `max_tokens=150` to guarantee total tokens per request stay around ~180-220 tokens, easily operating within the 8K TPM / 30 RPM budget.

2. **Grounded Generator (`backend/app/rag/generator.py`)**:
   - Initialize Groq client (`AsyncGroq`) with model `openai/gpt-oss-120b`.
   - Zero-temperature (`temperature=0.0`) system prompt clamped strictly to retrieved context.
   - Enforce facts-only answers with zero extrapolation or opinion generation.
   - Deterministic local fallback synthesis engine during external API degradation or rate limit throttling.

3. **Programmatic Output Validator (`backend/app/guardrails/output_validator.py`)**:
   - **Sentence Count Check**: Financial abbreviation-aware tokenizer enforcing $\le 3$ grammatically complete sentences.
   - **Single URL Citation**: Ensure exactly one verified official URL is present; inject canonical URL from metadata if absent or malformed.
   - **Timestamp Footer**: Ensure concluding line strictly matches: `Last updated from sources: YYYY-MM-DD`.

### Deliverables & Acceptance Criteria
- [x] Client-side quota limiter enforcing 30 RPM, 1K RPD, 8K TPM, 200K TPD.
- [x] Proactive zero-latency fallback when quotas are exhausted or on HTTP 429.
- [x] 100% of generated responses adhere to:
  - $\le 3$ sentences.
  - Exactly 1 valid citation URL.
  - Accurate timestamp footer.

---

## Phase 6: Backend API Layer (FastAPI)

### Objective
Expose high-performance, asynchronous REST endpoints with full Pydantic validation, Groq rate limiting telemetry, and CORS support.

### Key Tasks
1. **API Endpoints (`backend/app/api/endpoints.py`)**:
   - `POST /api/v1/chat/query`: Main end-to-end query execution endpoint coordinating all 4 tiers (PII, Intent Routing, Entity-Filtered Retrieval, Grounded LLM Generation).
   - `GET /api/v1/schemes`: Returns list of 5 supported HDFC schemes, categories, benchmarks, and Groww source links.
   - `GET /api/v1/health`: Diagnostic health check reporting vector index state and indexed chunk count.
   - `GET /api/v1/rate-limit`: Live Groq quota utilization metrics (RPM, TPM, RPD, TPD).
2. **Pydantic Schemas (`backend/app/schemas/chat.py`)**:
   - `ChatQueryRequest`: Non-empty stripped string validation (1–1000 characters).
   - `ChatQueryResponse`: Complete response contract (`status`, `query`, `intent`, `response`, `sentence_count`, `source_url`, `last_updated`, `disclaimer`, `is_fallback`, `latency_ms`).
   - `SchemeSummary`, `SchemeListResponse`, `HealthResponse`, `ErrorResponse`.
3. **Pipeline Orchestrator (`backend/app/api/chat_service.py`)**:
   - Encapsulates lifecycle management, startup pre-warming of vector embeddings, and end-to-end routing.
4. **Middleware & Exception Handling (`backend/main.py`)**:
   - CORS middleware for frontend communication.
   - Centralized validation and error handlers returning standardized JSON.
5. **API Test Suite (`backend/tests/test_api_endpoints.py`)**:
   - 10 automated async tests covering health, schemes, rate limits, factual queries, PII blocking, advisory refusal, comparison refusal, disambiguation, and validation errors.

### Deliverables & Acceptance Criteria
- [x] FastAPI application runs smoothly with full CORS and pre-warmed embeddings.
- [x] Interactive OpenAPI Swagger docs at `/docs` reflecting complete schema definitions.
- [x] `POST /api/v1/chat/query`, `GET /api/v1/schemes`, `GET /api/v1/health`, `GET /api/v1/rate-limit` fully functional.
- [x] 100% automated test coverage for API endpoints in `backend/tests/test_api_endpoints.py`.

---

## Phase 7: Automated Daily Ingestion Scheduler (GitHub Actions)

### Objective
Establish an automated daily data ingestion and index synchronization scheduler using **GitHub Actions**. The pipeline automatically crawls/scrapes official Groww scheme sources, normalizes and validates fund metrics, generates updated atomic knowledge chunks, computes dense embeddings, and refreshes the persistent ChromaDB vector store daily so the RAG assistant always operates on fresh, verified data with zero downtime.

### Pipeline Workflow & Architecture
```
┌────────────────────────────────────────────────────────────────────────┐
│             DAILY SCHEDULED INGESTION PIPELINE (00:00 UTC)             │
│                                                                        │
│  [ Cron: 0 0 * * * ] / [ Manual workflow_dispatch ]                   │
│          │                                                             │
│          ▼                                                             │
│  1. Scraper (`scraper.py`) ──► Fetch fresh data from Groww Scheme URLs │
│          │                                                             │
│          ▼                                                             │
│  2. Parser & Validator ────► Pydantic Schema Validation (schemes.json) │
│          │                                                             │
│          ▼                                                             │
│  3. Atomic Chunker ────────► Generate 38 Chunks with ISO Date Footers  │
│          │                                                             │
│          ▼                                                             │
│  4. Vector Store Manager ──► Embeddings (MiniLM-L6-v2) & ChromaDB Sync │
│          │                                                             │
│          ▼                                                             │
│  5. Automated Verification ──► Pytest Accuracy Smoke Check & Git Sync  │
└────────────────────────────────────────────────────────────────────────┘
```

### Key Tasks
1. **GitHub Actions Workflow (`.github/workflows/daily_ingestion_scheduler.yml`)**:
   - **Cron Trigger**: Scheduled daily at 10:00 AM IST / 04:30 AM UTC (`cron: '30 4 * * *'`) and manual trigger (`workflow_dispatch`).
   - **Environment Setup**: Set up Python 3.10+, pip cache dependencies, and cache sentence-transformers weights (`all-MiniLM-L6-v2`).
   - **Automated Execution**: Run end-to-end ingestion CLI command (`python -m backend.app.rag.daily_ingestion`).
   - **Git Auto-Commit & Artifact Sync**: Automatically commit and push updated `data/processed/schemes.json`, `data/processed/chunks.json`, and ChromaDB metadata with semantic commit: `chore(data): daily automated scheme ingestion and chromadb re-indexing [skip ci]`.

2. **Automated Ingestion Orchestrator (`backend/app/rag/daily_ingestion.py`)**:
   - Coordinates the 5 pipeline stages sequentially:
     - **Stage 1 (Scraping)**: Scrape all 5 HDFC schemes from canonical Groww URLs.
     - **Stage 2 (Normalization & Validation)**: Parse, clean, and validate all fields against `SchemeMetadata` Pydantic models.
     - **Stage 3 (Chunking)**: Re-generate the 38 atomic chunks in `data/processed/chunks.json` with updated `last_updated` date.
     - **Stage 4 (Vector Store Re-indexing)**: Pre-compute 384-dim dense embeddings using `all-MiniLM-L6-v2` and reload collection `mutual_fund_facts` in ChromaDB.
     - **Stage 5 (Integrity Verification)**: Execute automated sanity checks to verify chunk count ($\ge 38$), non-empty embeddings, and retrieval query accuracy.

3. **Data Integrity & Validation Guardrails**:
   - **Validation Barrier**: If scraping fails or any required fund parameter (TER, Exit Load, Minimum SIP) is missing/corrupted, the pipeline halts immediately without modifying the active production vector store.
   - **Alerting & Audit Logs**: Detailed structured JSON logging of ingestion status, chunk diff count, and execution latency.

### Deliverables & Acceptance Criteria
- [x] `.github/workflows/daily_ingestion_scheduler.yml` configured and active.
- [x] Daily cron execution scheduled at `10:00 AM IST` (`30 4 * * *` UTC) with `workflow_dispatch` manual trigger.
- [x] Automated end-to-end pipeline: Scraping $\rightarrow$ Normalization $\rightarrow$ Chunking $\rightarrow$ Dense Embeddings $\rightarrow$ ChromaDB Re-indexing.
- [x] Strict schema validation prevents corrupt data from reaching the vector store.
- [x] Automated git commit / artifact update with fresh `Last updated from sources: YYYY-MM-DD` timestamps.

---

## Phase 8: Verification, Test Suite & Documentation

### Objective
Perform end-to-end automated testing, compliance auditing, and generate complete project documentation.

### Key Tasks
1. **Automated Test Suite (`backend/tests/`)**:
   - `test_pii_guardrails.py`: Test PAN, Aadhaar, OTP, and contact blocking.
   - `test_advisory_refusal.py`: Test refusal responses for advice/recommendation prompts.
   - `test_factual_accuracy.py`: Test factual queries across all 5 schemes (TER, Exit load, SIP, Lock-in, Riskometer, Benchmark).
   - `test_output_formatting.py`: Verify sentence count ($\le 3$), single link citation, and timestamp footer.
   - `test_api_endpoints.py`: Verify HTTP status codes, latency, and payload schemas.
2. **Project Documentation & Release Packaging**:
   - Create root [`README.md`](file:///Users/jeevanshu/Documents/Investment%20Assistant/Investment-Assistant/README.md) covering:
     - Project overview & core philosophy.
     - Quickstart setup instructions (`pip install`, run backend, open frontend).
     - Scheme directory and reference URLs.
     - Architecture summary & guardrails.
     - Known limitations & disclaimer snippet.

### Deliverables & Acceptance Criteria
- [ ] All Pytest test suites passing with 100% success rate.
- [ ] Complete `README.md` created at repository root.

---

## Summary of Implementation Artifacts

| Phase | Main Files Created / Modified | Purpose |
| :--- | :--- | :--- |
| **Phase 1** | `requirements.txt`, `.env.example`, `backend/app/core/config.py` | Environment and configuration scaffolding |
| **Phase 2** | `data/processed/schemes.json`, `backend/app/rag/chunker.py` | Official data curation and chunking |
| **Phase 3** | `backend/app/rag/vector_store.py`, `backend/app/rag/retriever.py` | Vector embeddings and dense retrieval |
| **Phase 4** | `backend/app/guardrails/pii_filter.py`, `intent_router.py`, `refusal_handler.py` | PII protection, intent routing, and refusals |
| **Phase 5** | `backend/app/rag/generator.py`, `backend/app/guardrails/output_validator.py` | LLM synthesis and 3-sentence formatting validator |
| **Phase 6** | `backend/app/api/endpoints.py`, `backend/app/schemas/chat.py`, `backend/main.py` | FastAPI REST service |
| **Phase 7** | `.github/workflows/daily_ingestion_scheduler.yml`, `backend/app/rag/daily_ingestion.py` | Daily automated scraping, normalization, chunking, and ChromaDB re-indexing scheduler |
| **Phase 8** | `backend/tests/test_*.py`, `README.md` | Pytest verification suite and project documentation |
