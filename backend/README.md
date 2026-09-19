# Ingatini Backend

FastAPI backend for the Ingatini RAG application: JWT auth, document
ingestion, pgvector search, and Gemini-powered answers.

## Quick start

### With Docker (from repo root)

```bash
docker compose up          # Postgres + backend with --reload
```

### Local

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # set GEMINI_API_KEY and JWT_SECRET
uvicorn main:app --reload
```

API and Swagger UI: http://localhost:8000/docs (routes are mounted under `/api`).

## Environment

| Variable | Required | Notes |
|----------|----------|-------|
| `DATABASE_URL` | yes | Postgres with pgvector |
| `GEMINI_API_KEY` | yes | Embeddings + LLM |
| `JWT_SECRET` | yes | Any long random string; tokens invalidate if it changes |
| `JWT_EXPIRE_MINUTES` | no | Default 1440 (24 h) |
| `GEMINI_EMBEDDING_MODEL` / `GEMINI_LLM_MODEL` | no | Defaults: `models/gemini-embedding-001`, `gemini-2.0-flash` |
| `DEBUG`, `LOG_LEVEL`, `CORS_ORIGINS` | no | See `app/core/config.py` |

## Layout

```
backend/
├── app/
│   ├── api/          # Routers: auth.py, documents.py, query.py, health.py; deps.py (get_current_user)
│   ├── core/         # config.py (env settings), database.py, security.py (JWT + bcrypt)
│   ├── models/       # SQLAlchemy models: User, Document, Chunk, QueryLog
│   ├── schemas/      # Pydantic request/response models
│   └── services/     # embedding_service, rag_service, document_parser,
│                     # text_processor, document_service, errors.py
├── tests/            # pytest suite
├── main.py           # App entry: CORS, create_all, router wiring
└── requirements.txt
```

## Testing

```bash
pytest            # from backend/, with the venv active
```

18 unit tests cover password/token handling, text chunking, and the embedding
service (dimension pinning, batching, retries) with a faked Gemini client —
no network or database needed. Full E2E walkthrough: [../docs/TESTING.md](../docs/TESTING.md).

## Notes

- Tables are created via `Base.metadata.create_all` at startup — dev-only
  convenience; production should use Alembic (pinned but unconfigured).
- Handlers are plain `def` on purpose: sync DB/Gemini work runs in FastAPI's
  threadpool instead of blocking the event loop.
- Upload pipeline rolls back the document row on any processing failure.
