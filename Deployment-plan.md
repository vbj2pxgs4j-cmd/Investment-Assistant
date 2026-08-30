# Mutual Fund FAQ Assistant - Deployment Plan

The detailed production deployment, containerization, and infrastructure documentation is maintained in:

👉 **[doc/Deployment-plan.md](file:///Users/jeevanshu/Documents/Investment%20Assistant/Investment-Assistant/doc/Deployment-plan.md)**

---

### Quick Summary
- **Topologies**: PaaS (Vercel + Render), Docker Compose (Self-hosted VM), Kubernetes.
- **Backend**: FastAPI + Uvicorn + ChromaDB + SentenceTransformers (`all-MiniLM-L6-v2`) + Groq LPU API.
- **Frontend**: React + Vite (Tailwind CSS, Lucide icons, SSE streaming).
- **Automated Scheduler**: Daily 10:00 AM IST ingestion cron via GitHub Actions (`.github/workflows/daily_ingestion_scheduler.yml`).
- **Health Probes**: `GET /api/v1/health` and `GET /api/v1/rate-limit`.
