# System Architecture: Mutual Fund FAQ Assistant (Facts-Only RAG)

---

## 1. Architecture Overview & Design Principles

The **Mutual Fund FAQ Assistant** is a specialized, compliance-first Retrieval-Augmented Generation (RAG) system designed to deliver verified, factual mutual fund scheme data. Built around the reference product paradigm of **Groww**, the system operates under a strict **"Accuracy Over Intelligence"** principle.

### Key Architectural Tenets
1. **Zero Advisory Hallucination**: Strict pre-retrieval and post-generation guardrails prevent opinions, stock picks, or return predictions.
2. **Deterministic Attribution**: Every factual answer is linked to exactly one verified Groww scheme source URL (`groww.in/mutual-funds/...`).
3. **Format Conformance Guarantee**: Hard programmatic constraints enforce a 3-sentence maximum limit and a mandatory source timestamp footer.
4. **Zero PII Exposure**: Absolute refusal to ingest, process, or store sensitive financial or personal identity data (PAN, Aadhaar, account numbers, OTPs).

---

## 2. High-Level System Architecture

```mermaid
flowchart TB
    subgraph ClientTier ["1. Presentation Layer (UI/Client)"]
        UI["Web / Chat Interface<br/>(Groww Design Language)"]
        Disclaimer["Persistent Disclaimer<br/>'Facts-only. No investment advice.'"]
        Chips["Interactive Starter Prompt Chips"]
    end

    subgraph GatewayTier ["2. API Gateway & Security Layer"]
        API["FastAPI / Backend Router"]
        PIIFilter["PII Scrubber & Regex Detector<br/>(PAN, Aadhaar, OTPs, Phone, Email)"]
        RateLimiter["Rate Limiting & Request Validator"]
    end

    subgraph GuardrailTier ["3. Query Routing & Compliance Guardrails"]
        Router["Intent Classifier / Policy Router"]
        RefusalHandler["Refusal Engine<br/>(Groww Education / Guidelines Link)"]
        PerfHandler["Performance Query Interceptor<br/>(Direct Groww Scheme Linker)"]
    end

    subgraph RAGTier ["4. Retrieval & Knowledge Engine"]
        Retriever["Hybrid / Dense Semantic Retriever"]
        MetaFilter["Metadata Filter<br/>(Scheme: Mid-Cap, Small-Cap, etc.)"]
        VectorDB["Vector Database / Index<br/>(ChromaDB / FAISS / Qdrant)"]
        DocCorpus[("Groww Scheme Corpus Store<br/>(5 HDFC Scheme URLs from Groww)")]
    end

    subgraph LLMTier ["5. Generation & Output Enforcement"]
        PromptEngine["System Prompt Grounding Engine"]
        LLM["Groq LLM Engine<br/>(Llama-3.3-70b / Llama-3.1-8b via Groq API)"]
        OutputValidator["Output Constraint Validator<br/>- ≤ 3 Sentences<br/>- Exactly 1 URL<br/>- Timestamp Footer"]
    end

    %% Flow Connections
    UI --> API
    Disclaimer -.-> UI
    Chips -.-> UI
    API --> PIIFilter
    PIIFilter --> RateLimiter
    RateLimiter --> Router

    Router -- "Advisory / Subjective Intent" --> RefusalHandler
    Router -- "Performance Return Query" --> PerfHandler
    Router -- "Valid Factual Scheme Query" --> MetaFilter

    RefusalHandler --> API
    PerfHandler --> API

    MetaFilter --> Retriever
    DocCorpus --> VectorDB
    VectorDB --> Retriever
    Retriever --> PromptEngine
    PromptEngine --> LLM
    LLM --> OutputValidator
    OutputValidator --> API
    API --> UI
```

---

## 3. End-to-End Component Breakdown

### 3.1 Corpus & Source Model (Groww Scheme URLs)
The knowledge corpus is built exclusively from **verified Groww scheme pages**, establishing a single authoritative ground-truth source model.

#### Canonical Groww Scheme URLs:
| Scheme Name | Category | Canonical Groww Source URL |
| :--- | :--- | :--- |
| **HDFC Mid-Cap Opportunities Fund** | Equity: Mid Cap | `https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth` |
| **HDFC Small Cap Fund** | Equity: Small Cap | `https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth` |
| **HDFC Gold ETF Fund of Fund** | Commodities: FoF | `https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth` |
| **HDFC Top 100 / Large Cap Fund** | Equity: Large Cap | `https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth` |
| **HDFC ELSS Tax Saver Fund** | Equity: ELSS | `https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth` |

```mermaid
flowchart LR
    A["Groww Scheme Pages<br/>(5 Curated Groww URLs)"] --> B["Groww Data Extractor<br/>(HTML / Structured Parser)"]
    B --> C["Parameter-Aware Chunking<br/>(Expense Ratio, Exit Load, Min SIP, etc.)"]
    C --> D["Metadata Tagging<br/>(scheme, category, param, groww_url, date)"]
    D --> E["Embedding Model<br/>(e.g., text-embedding-004 / MiniLM)"]
    E --> F[("Vector Store<br/>Chroma / FAISS")]
```

#### Chunking & Metadata Strategy
Documents are partitioned by **factual parameter domains** (e.g., Exit Load, Expense Ratio, Investment Limits, Riskometer, Benchmark) directly aligned with Groww scheme specifications. Each chunk contains structured metadata linking directly to its respective Groww page:
```json
{
  "chunk_id": "hdfc_small_cap_exit_load_v1",
  "scheme_name": "HDFC Small Cap Fund",
  "scheme_code": "hdfc-small-cap-fund-direct-growth",
  "category": "Equity: Small Cap",
  "parameter": "exit_load",
  "content": "For units redeemed within 1 year from the date of allotment, an exit load of 1.00% is applicable. No exit load is payable for units redeemed after 1 year.",
  "official_source_url": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
  "primary_source_doc": "Groww Scheme Page (HDFC Small Cap Fund Direct Growth)",
  "last_updated": "2024-04-01"
}
```

---

### 3.2 Pre-Retrieval Guardrails & Query Routing

Every incoming prompt undergoes a 3-stage validation pipeline before invoking LLM retrieval:

```mermaid
flowchart TD
    Q["User Input Query"] --> S1{"1. PII Detected?<br/>(PAN, Aadhaar, OTP, Phone)"}
    S1 -- Yes --> R1["Refusal: Security Warning & Zero PII Logging"]
    S1 -- No --> S2{"2. Advisory / Opinion Intent?<br/>('Should I invest?', 'Which is better?')"}
    S2 -- Yes --> R2["Refusal: Non-Advisory Notice + Groww Guide Link"]
    S2 -- No --> S3{"3. Custom Return / Performance Calc?"}
    S3 -- Yes --> R3["Direct Groww Scheme Page Response"]
    S3 -- No --> S4["Proceed to Scheme Entity & Factual Retrieval"]
```

| Guardrail Module | Detection Mechanism | Action / Output |
| :--- | :--- | :--- |
| **PII Scrubber** | Regex + Name Entity Recognition (NER) for PAN (`[A-Z]{5}[0-9]{4}[A-Z]`), Aadhaar (`\d{4}\s?\d{4}\s?\d{4}`), Phone, OTPs. | Immediate block. Do not record query in logs. |
| **Advisory Classifier** | Zero-shot intent classification / Rule-based pattern matching (e.g., *"recommend"*, *"best"*, *"should I"*, *"target return"*). | Standard refusal template + [Groww Mutual Funds Guidelines](https://groww.in/mutual-funds). |
| **Performance Interceptor** | Keywords: *"how much return"*, *"calculate 10k in 5 years"*, *"CAGR compare"*. | Provide corresponding Groww scheme URL citation only; block mathematical projections. |
| **Entity Resolver** | Fuzzy matching over the 5 target HDFC schemes. | Injects scheme metadata filter into vector retriever. |

---

### 3.3 Retrieval & Context Assembly

1. **Query Expansion & Normalization**: The raw user query (e.g., *"hdfc tax saver lock in"*) is normalized and matched to canonical scheme keys (`hdfc-elss-tax-saver-fund-direct-plan-growth`) and parameter type (`lock_in_period`).
2. **Dense Vector Retrieval + Metadata Pre-filtering**:
   $$\text{Score}(q, d) = \text{CosineSimilarity}(\mathbf{e}_q, \mathbf{e}_d) \quad \text{subject to} \quad d.\text{scheme} = \text{ResolvedScheme}$$
3. **Context Assembly**: Top-$k$ chunks ($k=1$ to $2$) are passed to the prompt synthesizer with the authoritative source link.

---

### 3.4 Generation & Output Conformance Layer

The generation engine uses strict system prompting paired with post-generation deterministic validation.

#### System Prompt Blueprint
```text
You are a facts-only Mutual Fund FAQ Assistant for HDFC Mutual Fund schemes.
You provide objective, verifiable information sourced exclusively from the provided context.

STRICT OPERATIONAL RULES:
1. Provide factual information ONLY. Do NOT give investment advice, opinions, or recommendations.
2. Answer in NO MORE THAN 3 SENTENCES.
3. Every response MUST cite exactly ONE official source URL provided in the context.
4. Conclude EVERY response with:
   Last updated from sources: <date from context>
5. If the question cannot be answered purely from the provided context, state that clearly.
```

#### Output Validator Pipeline
```mermaid
flowchart TD
    LLM_OUT["LLM Raw Output"] --> V1{"Sentence Count ≤ 3?"}
    V1 -- No --> A1["Deterministic Splitter & Truncate to 3 Sentences"]
    V1 -- Yes --> V2{"Valid Single Source URL Present?"}
    A1 --> V2
    V2 -- No --> A2["Inject Canonical Source URL from Context Metadata"]
    V2 -- Yes --> V3{"Timestamp Footer Present?"}
    A2 --> V3
    V3 -- No --> A3["Append 'Last updated from sources: <date>'"]
    V3 -- Yes --> FINAL["Deliver Conforming Response to Client"]
    A3 --> FINAL
```

---

## 4. Sequence Diagrams

### 4.1 Factual Query Flow
```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Web Frontend
    participant API as Gateway / App
    participant Guard as Guardrail / Router
    participant Retriever as Vector Retriever
    participant Store as Corpus / VectorDB
    participant LLM as LLM Engine
    participant Post as Output Validator

    User->>UI: "What is the exit load for HDFC Small Cap Fund?"
    UI->>API: POST /api/v1/query {query: "..."}
    API->>Guard: Validate PII & Query Intent
    Guard-->>API: Intent = FACTUAL, Scheme = HDFC Small Cap
    API->>Retriever: Retrieve(query, filter={scheme: "hdfc-small-cap"})
    Retriever->>Store: Query embedding vector
    Store-->>Retriever: Relevant Chunk + Metadata (Exit Load 1%, 1 Year, URL, Date)
    Retriever-->>API: Top Context + Metadata
    API->>LLM: Generate constrained response(Context, Query)
    LLM-->>Post: Raw Generated Response
    Post->>Post: Verify sentence count ≤ 3, 1 URL, valid timestamp
    Post-->>API: Verified Conforming Response
    API-->>UI: {text, source_url, last_updated}
    UI-->>User: Displays 3-sentence factual card with citation badge & timestamp
```

### 4.2 Advisory Query Refusal Flow
```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Web Frontend
    participant API as Gateway / App
    participant Guard as Guardrail / Router

    User->>UI: "Should I invest 50,000 in HDFC Mid-Cap Fund for 3 years?"
    UI->>API: POST /api/v1/query {query: "..."}
    API->>Guard: Evaluate Intent
    Guard-->>API: Intent = ADVISORY_DETECTED (Flagged: "Should I invest")
    API-->>UI: {text: "I cannot provide investment recommendations or financial advice. I am a facts-only assistant designed to answer objective scheme queries.", source_url: "https://groww.in/mutual-funds", last_updated: "2024-04-01"}
    UI-->>User: Renders Polite Refusal Card + Groww Mutual Funds Resource Link
```

---

## 5. Data Flow & API Contracts

### 5.1 Query Endpoint
`POST /api/v1/chat/query`

#### Request Payload
```json
{
  "query": "What is the minimum SIP amount for HDFC Mid-Cap Opportunities Fund?",
  "session_id": "sess_anon_98234"
}
```

#### Response Payload (Factual)
```json
{
  "status": "success",
  "type": "factual",
  "response": "The minimum SIP investment amount for HDFC Mid-Cap Opportunities Fund (Direct - Growth) is ₹100 per installment. Investors can also invest a minimum lump sum amount of ₹100 for additional purchases. All investments remain subject to applicable scheme terms.",
  "sentence_count": 3,
  "source_url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
  "last_updated": "2024-04-01",
  "disclaimer": "Facts-only. No investment advice."
}
```

#### Response Payload (Refusal)
```json
{
  "status": "refusal",
  "type": "advisory_blocked",
  "response": "I cannot provide investment advice, scheme comparisons, or opinions on whether a fund is suitable for you. You can review verified factual fund parameters or consult a SEBI-registered financial advisor.",
  "sentence_count": 2,
  "source_url": "https://groww.in/mutual-funds",
  "last_updated": "2024-04-01",
  "disclaimer": "Facts-only. No investment advice."
}
```

---

## 6. Technical Stack & Module Mapping

| Layer | Recommended Technology | Purpose & Rationale |
| :--- | :--- | :--- |
| **Frontend** | HTML5, Vanilla CSS3 / Modern JS (or React) | Lightweight, instantaneous load times, Groww-style dark/light UI, persistent disclaimers. |
| **Backend API** | Python (FastAPI / Uvicorn) | High-performance asynchronous API, lightweight middleware routing, native Pydantic validation. |
| **Vector Store** | ChromaDB / FAISS / In-Memory JSON Index | Lightweight, local embedded store requiring zero external cloud database overhead for 5 scheme corpora. |
| **Embeddings** | Google `text-embedding-004` or `all-MiniLM-L6-v2` | High-fidelity dense retrieval for financial scheme nomenclature. |
| **LLM Inference** | Groq API (`groq` SDK with `llama-3.3-70b-versatile` / `llama-3.1-8b-instant`) | Ultra-fast LPU inference, near-instant TTFT, high-precision constrained text synthesis. |
| **Guardrails & Testing** | Pytest, Guardrails AI / Pydantic Validators | Deterministic validation of sentence counts, links, and PII masking. |

---

## 7. Security, Privacy & Reliability Matrix

| Category | Measure | Implementation Mechanism |
| :--- | :--- | :--- |
| **PII Protection** | Zero Data Ingestion | Pre-flight regex filtering strips PAN, Aadhaar, account numbers, and phone numbers before state persistence. |
| **Regulatory Guard** | Mandatory Disclaimer | Frontend forces a sticky disclaimer banner across all viewport states. |
| **Hallucination Control** | Strict Context Clamping | Temperature set to `0.0`; LLM prompt strictly rejects extrapolating beyond supplied text chunks. |
| **Link Integrity** | Groww Source Whitelisting | All scheme citations and educational links are strictly validated against verified Groww URLs (`https://groww.in/mutual-funds/...`). |
| **Telemetry** | Anonymous Metrics | Aggregates factual vs. refused queries count without logging user prompts or identifiable metadata. |
