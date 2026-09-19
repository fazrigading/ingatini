# Getting Started

Setup guide for developing and running Ingatini. For what the app does, see the
[README](../README.md); for endpoint details, see [API.md](API.md).

## Prerequisites

- Docker & Docker Compose (recommended path)
- Node.js 18+ (frontend dev)
- Python 3.11+ (local backend dev only)
- A [Gemini API key](https://ai.google.dev/)

## Quick start (Docker)

```bash
# 1. Clone and configure
git clone https://github.com/fazrigading/ingatini.git && cd ingatini
cp .env.example .env          # add your GEMINI_API_KEY

# 2. Backend + database
docker compose up

# 3. Frontend (new terminal)
cd frontend
npm install                   # first time only
npm run dev
```

| URL | What |
|-----|------|
| http://localhost:5173 | Frontend app |
| http://localhost:8000/api | Backend API |
| http://localhost:8000/docs | Swagger UI |

Then register an account in the UI and upload your first document. The full
walkthrough (including multi-user isolation checks) is in
[docs/TESTING.md](TESTING.md).

## Local development (without Docker)

### Database only

```bash
docker run -d --name ingatini_postgres \
  -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=ingatini_db \
  -p 5432:5432 pgvector/pgvector:pg15
```

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # add GEMINI_API_KEY + JWT_SECRET
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment variables

Backend (`.env` at repo root — also read by `backend/app/core/config.py`):

| Variable | Default | Notes |
|----------|---------|-------|
| `DATABASE_URL` | `postgresql://user:password@localhost:5432/ingatini_db` | Postgres with pgvector |
| `GEMINI_API_KEY` | — | **Required** for uploads and queries |
| `JWT_SECRET` | — | **Required** for auth (compose provides an insecure dev default) |
| `JWT_EXPIRE_MINUTES` | `1440` | Token lifetime (24 h) |
| `GEMINI_EMBEDDING_MODEL` | `models/gemini-embedding-001` | Pinned to 768-dim output |
| `GEMINI_LLM_MODEL` | `gemini-2.0-flash` | Answer generation |
| `DEBUG` | `True` | Also toggles SQL echo — set `False` outside dev |
| `LOG_LEVEL` | `INFO` | |
| `CORS_ORIGINS` | `["http://localhost:3000", "http://localhost:5173"]` | JSON list |
| `BACKEND_HOST` / `BACKEND_PORT` | `0.0.0.0` / `8000` | |

Frontend (`frontend/.env`):

| Variable | Default | Notes |
|----------|---------|-------|
| `VITE_API_BASE_URL` | `http://localhost:8000/api` | Backend URL |

## Development commands

```bash
# Dev helper (wraps docker compose)
./scripts/dev start | stop | rebuild | logs | shell | test | format | lint

# Backend tests
cd backend && pytest

# Frontend
cd frontend
npm run dev        # dev server with HMR
npm run build      # production build → dist/
npm run preview    # serve the production build
npm run lint
```

## Troubleshooting

**Docker**
```bash
docker compose down -v          # full reset (deletes data!) — needed once after
docker compose up --build       # pulling the auth changes (schema changed)
docker compose logs -f backend
```

**Port conflicts** — backend: change `BACKEND_PORT`; frontend:
`npm run dev -- --port 5174`.

**Database inspection**
```bash
docker compose exec postgres psql -U user -d ingatini_db
# then: \dt  (tables),  \dx  (pgvector extension)
```

**401 everywhere in the frontend** — token expired; log out and back in. If it
persists, clear localStorage (`ingatini_token`) and check that `JWT_SECRET`
hasn't changed since the token was issued.

**Upload fails with 502** — Gemini API key invalid or quota exhausted; check
`docker compose logs backend`.

## Resources

- [FastAPI](https://fastapi.tiangolo.com/) · [React](https://react.dev/) · [Vite](https://vitejs.dev/)
- [pgvector](https://github.com/pgvector/pgvector) · [Gemini API docs](https://ai.google.dev/docs)

## License

MIT
