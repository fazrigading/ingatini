# Implementation Status

What is implemented today, and what's next. Architecture details live in
[docs/ARCHITECTURE.md](ARCHITECTURE.md).

## Status

| Area | Status | Notes |
|------|--------|-------|
| Backend API (FastAPI) | ✅ Complete | Auth, documents, query, health — see [docs/API.md](API.md) |
| JWT authentication | ✅ Complete | Register/login/me, bcrypt hashing, token-derived identity, ownership checks |
| Embedding pipeline | ✅ Complete | `gemini-embedding-001` @ 768-d, batched with retry/backoff |
| RAG query engine | ✅ Complete | Owner-scoped cosine search, 0.5 similarity threshold, Gemini answers |
| Frontend (React/Vite) | ✅ Complete | Login/register, upload, chat with source scores, history, delete |
| Tests | ✅ In place | 18 unit tests: security, text processing, embeddings |
| Deployment | ⬜ Not started | Checklist in [docs/DEPLOYMENT.md](DEPLOYMENT.md) |
| Alembic migrations | ⬜ Not started | Schema currently via `create_all` (dev-only) |

## Key implementation decisions

- **Token identity everywhere** — no endpoint trusts a client-supplied `user_id`;
  `get_current_user` resolves the caller and all queries filter by ownership.
  Vector search joins `Document.user_id`, closing the cross-user leak.
- **768-dim embeddings** — `gemini-embedding-001` defaults to 3072 dimensions;
  `output_dimensionality=768` is pinned to match the `Vector(768)` column and
  keep storage small.
- **Cosine similarity threshold** — search uses `<=>` and drops chunks below
  0.5 similarity, so the "no relevant information" path is real instead of
  feeding noise to the LLM.
- **Batched embeddings** — one Gemini call per document with retry/backoff;
  upload cost is O(1) API round-trips, not O(chunks).
- **Typed service errors** — `EmbeddingError`/`LLMError`/`ParsingError` map to
  502/502/400 respectively; raw exception strings never reach clients.
- **Sentence-aligned chunking** — ~1024-char chunks with 100-char overlap,
  cut on sentence boundaries; `clean_text` preserves punctuation and URLs.

## Roadmap

### Near term
- [ ] Production deployment (see [docs/DEPLOYMENT.md](DEPLOYMENT.md))
- [ ] Alembic migrations replacing `create_all`
- [ ] Rewrite or remove `backend/test_rag_pipeline.py` (targets the pre-auth API)

### Later / ideas
- [ ] Multiple document collections per user
- [ ] Advanced search & filtering
- [ ] Analytics dashboard over QueryLogs
- [ ] n8n automation (upload triggers embedding pipeline)
- [ ] Dark mode toggle
- [ ] Rate limiting / quotas beyond upload limits
