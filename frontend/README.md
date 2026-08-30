# Mutual Fund FAQ Assistant - React Frontend (Vite)

This is the modern React web frontend for the **HDFC Mutual Fund FAQ Assistant**, built using the **Google Stitch "Luminous Fintech"** design system inspired by **Groww**.

---

## Features
- **Design System**: Deep slate dark mode (`#0b1326`), Groww Emerald (`#00D09C` / `#44EDB7`), glassmorphic panels, and neon glow accents.
- **Typography**: Google Fonts **Outfit** (headings), **Plus Jakarta Sans** (body & UI), and **JetBrains Mono** (mono metrics).
- **FastAPI Integration**: Connects to `POST /api/v1/chat/query`, `GET /api/v1/schemes`, `GET /api/v1/health`, and `GET /api/v1/rate-limit`.
- **Safety Safeguards**: Prominent regulatory disclaimer, zero-PII security alerts, and non-advisory refusal badges.
- **Telemetry Modal**: Live visibility into Groq 30 RPM, 8K TPM, 1K RPD, and 200K TPD quota usage.

---

## Running with Vite Development Server

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start the development server**:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000). Requests to `/api/v1` are automatically proxied to the backend running on `http://localhost:8000`.

---

## Production Build

```bash
npm run build
```

The output will be built into the `dist/` directory, ready to be deployed or served statically by FastAPI.
