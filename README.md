# Ingatini — Personal Knowledge Search Engine

A Retrieval-Augmented Generation (RAG) application: upload documents, ask
AI-powered questions about them, and get answers with source attribution.
Built with FastAPI, PostgreSQL + pgvector, Google Gemini, and React.

## How it works

1. Register an account and log in (JWT-secured)
2. Upload documents (PDF, DOCX, TXT — up to 10 MB)
3. The backend extracts text, chunks it sentence-by-sentence, and stores
   768-dim Gemini embeddings in PostgreSQL with pgvector
4. Ask questions in the chat interface — the pipeline retrieves the most
   similar chunks from **your** documents and has Gemini answer with context
5. Every answer cites its sources with similarity scores; full query history is kept

## Features

- **JWT authentication** — register/login, per-user data isolation at the API and vector-search level
- **Document upload** — PDF, DOCX, TXT with size/type validation and rollback on processing failure
- **RAG Q&A** — owner-scoped cosine similarity search (threshold 0.5), batched embeddings with retry
- **Query history** — searchable log of past questions, answers, and chunk counts
- **Document management** — list and delete your uploads

## Quick start

Prerequisites: Docker, Node.js 18+, a [Gemini API key](https://ai.google.dev/).

```bash
# 1. Configure
cp .env.example .env            # then add your GEMINI_API_KEY

# 2. Start backend + database
docker compose up

# 3. Start frontend (new terminal)
cd frontend && npm install && npm run dev
```

- Frontend: http://localhost:5173
- API: http://localhost:8000/api — Swagger docs at http://localhost:8000/docs

> Already ran a previous version? The schema changed (`users.password_hash`).
> Reset the dev database once: `docker compose down -v` before `up`.

For local development without Docker, see [GETTING_STARTED.md](docs/GETTING_STARTED.md).

## Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI |
| Database | PostgreSQL 15 + pgvector |
| Embeddings | `gemini-embedding-001` @ 768-dim |
| LLM | `gemini-2.0-flash` |
| Auth | JWT (HS256) + bcrypt |
| Frontend | React 19 + Vite 7 + Tailwind CSS 4 |

## Configuration

All settings come from environment variables (`.env`, see `.env.example`):
`DATABASE_URL`, `GEMINI_API_KEY`, `JWT_SECRET`, `GEMINI_EMBEDDING_MODEL`,
`GEMINI_LLM_MODEL`, `CORS_ORIGINS`, and friends. Full list in
[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md).

## Documentation

| Doc | Contents |
|-----|----------|
| [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) | Setup, env vars, dev workflow, troubleshooting |
| [docs/API.md](docs/API.md) | Full API reference with examples |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Stack, request flows, data model, layout |
| [docs/TESTING.md](docs/TESTING.md) | Unit tests + end-to-end walkthrough |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Production checklist |
| [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md) | Implementation status & roadmap |
| [backend/README.md](backend/README.md) | Backend development |
| [frontend/README.md](frontend/README.md) | Frontend development |

## Development helpers

```bash
./dev start      # start the stack
./dev logs       # tail logs
./dev test       # run backend tests
./dev stop       # stop everything
```

## License

MIT
