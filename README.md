# Mutual Fund FAQ Assistant (Facts-Only RAG)

> **"Facts-only. No investment advice."**  
> An ultra-reliable, compliance-first Retrieval-Augmented Generation (RAG) assistant for HDFC Mutual Fund schemes with Groww as the reference product context.

---

## 🌟 Key Architectural Principles

1. **Zero Advisory Hallucination**: Strict pre-retrieval and post-generation guardrails prevent opinions, stock picks, or return predictions.
2. **Deterministic Attribution**: Every factual answer is verified by exactly one authoritative Groww scheme citation URL (`groww.in/mutual-funds/...`).
3. **Strict Formatting Conformance**: Programmatic enforcement ensures:
   - Maximum 3 sentences.
   - Exactly 1 verified Groww source citation link.
   - Concluding timestamp footer: `Last updated from sources: YYYY-MM-DD`.
4. **Zero PII Storage**: Pre-flight regex filtering immediately intercepts PAN, Aadhaar, contact details, and OTPs before LLM or retrieval invocation.

---

## 📁 Repository Layout

```
Investment-Assistant/
├── backend/
│   ├── app/
│   │   ├── api/          # Route handlers (chat, health, schemes)
│   │   ├── core/         # Settings (Pydantic), logging, constants
│   │   ├── guardrails/   # PII filter, advisory classifier, output validator
│   │   ├── rag/          # Ingestion, embeddings, retriever, generator
│   │   └── schemas/      # Pydantic request/response models
│   ├── tests/            # Automated Pytest suite
│   └── main.py           # FastAPI server entrypoint
├── data/
│   ├── raw/              # Extracted raw scheme documentation
│   ├── processed/        # Structured JSON scheme parameters
│   └── vector_store/     # Persistent ChromaDB index
├── frontend/
│   ├── index.html        # Responsive single-page chat UI
│   ├── styles.css        # Groww-inspired theme
│   └── app.js            # Client-side chat logic & prompt chips
├── doc/                  # Centralized system documentation
│   ├── Architecture.md
│   ├── edge-case.md
│   ├── eval.md
│   ├── implementation-plan.md
│   └── problemStatement.md
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # Project overview & documentation
```

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- Python 3.10+
- Virtual Environment (`venv` or `conda`)

### 2. Setup Virtual Environment & Install Dependencies
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env and supply your GROQ_API_KEY
```

### 4. Run Backend Service
```bash
uvicorn backend.main:app --reload --port 8000
```
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 🎯 Target Schemes & Categories

| # | Scheme Name | Category | Primary Reference URL |
| :-: | :--- | :--- | :--- |
| 1 | **HDFC Mid-Cap Opportunities Fund** | Equity: Mid Cap | `https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth` |
| 2 | **HDFC Small Cap Fund** | Equity: Small Cap | `https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth` |
| 3 | **HDFC Gold ETF Fund of Fund** | Commodities: FoF | `https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth` |
| 4 | **HDFC Top 100 / Large Cap Fund** | Equity: Large Cap | `https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth` |
| 5 | **HDFC ELSS Tax Saver Fund** | Equity: ELSS | `https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth` |

---

## ⚖️ Regulatory Disclaimer
**Facts-only. No investment advice.**  
This application provides objective, factual information extracted exclusively from verified Groww scheme pages and AMC/SEBI public filings. It does not provide personalized investment advice, stock recommendations, or return projections.
