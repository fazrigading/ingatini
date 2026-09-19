# Architecture

How Ingatini is built: stack, request flow, data model, and project layout.

## Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI (Python) |
| Database | PostgreSQL 15 + pgvector |
| ORM | SQLAlchemy 2.0 |
| Embeddings | Google Gemini `gemini-embedding-001` @ 768 dimensions |
| LLM | Google Gemini `gemini-2.0-flash` |
| Auth | JWT (HS256) + bcrypt password hashing |
| Frontend | React 19 + Vite 7 + Tailwind CSS 4 + Axios |
| Containers | Docker Compose (dev) |

## Request flows

### Document upload

```
POST /api/documents/upload (Bearer token, multipart file)
  → validate extension + 10 MB limit
  → create Document row
  → extract text (pypdf / python-docx / utf-8 txt)
  → sentence-aligned chunking (~1024 chars, 100-char overlap)
  → batched Gemini embeddings (output_dimensionality=768, retry + backoff)
  → store Chunks with vectors in pgvector
  → on any failure: document row is rolled back, error mapped to 4xx/5xx
```

### Query

```
POST /api/query (Bearer token)
  → embed the question (same model, 768-d)
  → pgvector cosine distance search (<=>) scoped to the caller's documents
  → keep chunks with similarity >= 0.5, best first, up to top_k
  → build context block → Gemini generate_content
  → log the exchange to QueryLogs
  → answer + per-chunk similarity scores
```

Search is always scoped by `Document.user_id` — a query can never touch another
user's chunks, even when `document_ids` is omitted.

## Data model

| Table | Purpose |
|-------|---------|
| `users` | Account (username, email, bcrypt password hash) |
| `documents` | Uploaded file metadata, owner, chunk count |
| `chunks` | Text segments with 768-dim embeddings, ordered by `chunk_index` |
| `query_logs` | Query/response history with retrieved-chunk counts |

Tables are created at startup via `Base.metadata.create_all` (no migrations yet —
see `docs/DEPLOYMENT.md` for the production caveat).

## Project structure

```
ingatini/
├── backend/
│   ├── app/
│   │   ├── api/              # Routers: auth, documents, query, health (+ deps.py)
│   │   ├── core/             # config.py (env settings), database.py, security.py (JWT/bcrypt)
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic request/response models
│   │   └── services/         # embedding_service, rag_service, document_parser,
│   │                         # text_processor, document_service, errors.py
│   ├── tests/                # pytest suite (security, text processing, embeddings)
│   ├── main.py               # App entry point, CORS, create_all
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/       # DocumentUpload, ChatInterface, QueryHistory
│   │   ├── services/api.js   # Axios client, token storage + interceptors
│   │   ├── App.jsx           # Session state, layout, document list
│   │   └── index.css         # Tailwind 4 entry
│   ├── package.json
│   ├── vite.config.js
│   ├── postcss.config.js
│   └── Dockerfile            # Production build; compose overrides to dev server
│
├── docs/                     # This documentation
├── docker-compose.yml        # Dev environment (Postgres + backend + frontend)
├── dev                       # Dev helper CLI
└── scripts/                  # dev CLI + start.sh (cd to repo root)
```

## Key design points

- **Token identity**: routers never trust a client-supplied `user_id`; identity
  comes from `get_current_user` (`backend/app/api/deps.py`).
- **Error taxonomy**: services raise `EmbeddingError` / `LLMError` / `ParsingError`
  (`backend/app/services/errors.py`) so routers can map outages to 502 instead of
  masking them as 404/500.
- **Embedding dimension**: pinned to 768 via `output_dimensionality` to match the
  `Vector(768)` column without storing 3072-dim vectors.
- **Sync handlers**: DB/Gemini work runs in plain `def` handlers so FastAPI runs
  them in its threadpool instead of blocking the event loop.
- **Frontend session**: JWT in `localStorage`, attached by an Axios request
  interceptor; a 401 response clears the session and returns to the login form.
