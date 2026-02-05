# Smart Underwriter

AI-assisted underwriting for insurance claims. Upload multiple policy PDFs, chunk and store them in Pinecone, then analyze a claim against all uploaded policies. The system returns a structured report with decision, evidence, and risk level.

## What It Does
- Ingests multiple PDFs, chunks text, and stores embeddings + metadata in Pinecone.
- Searches across all stored policy chunks for a given claim.
- Uses Groq LLM to produce a structured analysis:
	- Status: likely-covered | excluded | needs-review
	- Evidence: citations with page + filename
	- Risk level: low | medium | high

## Repo Structure
- backend: FastAPI API, ingestion, vector store, and agent orchestration
- frontend: Vite + React UI for uploading policies and analyzing claims

## Architecture
The system has three major layers: UI, API, and Vector/LLM services.

**Data Flow (High Level)**
1) Upload PDFs in the UI.
2) Backend parses and chunks text, embeds each chunk, and upserts to Pinecone.
3) Claim analysis embeds the claim, queries Pinecone for relevant chunks, then sends them to the Groq LLM.
4) UI renders the structured result with evidence and risk level.

**Components**
- **Frontend (React)**
	- Uploads PDFs and claim text
	- Displays analysis output and evidence chunks
- **Backend (FastAPI)**
	- `/ingest`: parse + chunk + embed + upsert
	- `/analyze`: embed claim + retrieve + LLM analysis + response
- **Vector Store (Pinecone)**
	- Stores chunk embeddings and metadata (page, filename, policy_id, text)
- **LLM (Groq)**
	- Produces decision, rationale, citations, and risk level

**Flow Diagram (Text)**
```
UI (Upload PDF) -> FastAPI /ingest -> Chunk + Embed -> Pinecone
UI (Analyze Claim) -> FastAPI /analyze -> Embed Claim -> Pinecone Query
Pinecone Results -> Groq LLM -> Structured Analysis -> UI
```

## Requirements
- Python 3.10+ (backend)
- Node 18+ (frontend)
- Pinecone index (dimension 8 by default)
- Groq API key

## Local Setup

### Backend
```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend
```
cd frontend
npm install
npm run dev
```
Open http://localhost:5173

## API Endpoints
- POST /ingest?policy_id=policy-123
	- multipart file upload
- POST /analyze
	- JSON: { policy_id: "global", claim_text: "..." }
- GET /policies

## Pinecone Index
Create a Dense index with dimension 8 (matches hash embeddings by default). Use metric = cosine. Ensure PINECONE_INDEX and PINECONE_ENV match your Pinecone settings.

## Analysis Flow
1. Upload PDF: backend parses pages, chunks text, embeds, and upserts to Pinecone with metadata.
2. Analyze claim: backend embeds the claim, queries Pinecone, and sends retrieved chunks to the Groq LLM.
3. Response: decision, rationale, risk level, citations with page + filename + full chunk text.

## LangGraph
Set USE_LANGGRAPH=true to run the analysis via LangGraph (retrieve -> analyze -> critic). Otherwise it uses the same steps directly in the orchestrator.

## UI Overview
- Upload policies (toast notification on success).
- Enter claim text and analyze.
- Results show decision, risk, rationale, and a list of full chunks with highlighted quotes.

## Deployment

### Frontend (Vercel)
- Deploy frontend only.
- .vercelignore excludes backend and local artifacts.
- Set VITE_API_BASE to your backend URL.

### Backend (Render/Railway/Fly.io)
- Start command:
	uvicorn app.main:app --host 0.0.0.0 --port $PORT
- Add env vars from the .env section above.

## Troubleshooting
- Pinecone 400 errors: metadata cannot include null values; ensure ingest strips None values.
- 500 on /analyze: check Groq API key and Groq SDK version.
- Nothing in Pinecone: ensure VECTOR_STORE=pinecone and backend restarted.
- CORS errors: verify frontend uses correct VITE_API_BASE.
