# Deployment Guide

The current setup is development-grade. This checklist takes it to production.

## Before deploying

- [ ] **Migrations**: schema is currently created by `Base.metadata.create_all` at
      startup. Set up Alembic (already in `requirements.txt`) before evolving the
      schema in production.
- [ ] **Secrets**: set strong, unique `JWT_SECRET` (e.g. `openssl rand -hex 32`),
      `DATABASE_URL`, and `GEMINI_API_KEY` from a secret manager — never commit `.env`.
- [ ] **`DEBUG=false`** — the default `DEBUG=True` also enables SQL echo logging.
- [ ] **CORS**: set `CORS_ORIGINS` to the real frontend origin(s).
- [ ] **Database**: managed PostgreSQL with the `pgvector` extension (or the
      `pgvector/pgvector` image), connection pooling (SQLAlchemy pool is
      configured: pool_size 10, max_overflow 20), and scheduled backups.
- [ ] **HTTPS/SSL** in front of both backend and frontend.
- [ ] **Rate limiting** on auth and upload endpoints (e.g. `slowapi` or a proxy).
- [ ] **Monitoring/logging**: ship uvicorn + app logs; the health endpoint
      (`GET /api/health`) reports DB connectivity for probes.
- [ ] **Upload limits**: already enforced in-app (10 MB, `.pdf/.docx/.txt`);
      mirror the limit at the proxy layer.

## Backend

- Build the `backend/` image, run with uvicorn behind a reverse proxy
  (`uvicorn main:app --host 0.0.0.0 --port 8000`, no `--reload`).
- Required env vars: `DATABASE_URL`, `GEMINI_API_KEY`, `JWT_SECRET`,
  `JWT_EXPIRE_MINUTES` (defaults fine), `DEBUG=false`, `LOG_LEVEL=INFO`,
  `CORS_ORIGINS`.

## Frontend

- `npm run build` produces `dist/`; serve it statically (the `frontend/Dockerfile`
  builds it and defaults to `vite preview` — swap for nginx/static hosting).
- Required env at build time: `VITE_API_BASE_URL` pointing at the production API.
- The Dockerfile bakes `VITE_API_BASE_URL` at build time — pass it as a build arg.

## Post-deploy

- [ ] Smoke test: register → login → upload → query → history
- [ ] Verify token expiry behavior (`JWT_EXPIRE_MINUTES`, default 24 h)
- [ ] Confirm Gemini quota/alerts
- [ ] Backups restore drill for the database
