# Testing

## Backend unit tests

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r <(echo "pytest")
# or: pip install -r requirements.txt pytest

pytest
```

Coverage today (18 tests):

- `tests/test_security.py` — password hashing, JWT round-trip, tampered/expired tokens
- `tests/test_text_processor.py` — punctuation-preserving cleaning, sentence-aligned chunking, overlap
- `tests/test_embedding_service.py` — dimension pinning, batched calls, retry/backoff, error typing

`tests/conftest.py` sets `JWT_SECRET` / `GEMINI_API_KEY` test defaults; the
embedding tests fake `genai.embed_content`, so no network or API key is needed.

## End-to-end walkthrough

Start the stack:

```bash
docker compose up          # backend + Postgres
cd frontend && npm run dev # in another terminal
```

Then walk the user journey at http://localhost:5173:

1. **Register** — create an account (username, email, password ≥ 8 chars)
2. **Log in** — you should land on the app with "Welcome, <username>!"
3. **Upload a document** — PDF, DOCX, or TXT; the badge shows the chunk count
4. **Ask a question** about the document content — the answer cites sources with similarity percentages
5. **Ask an unrelated question** — should return "No relevant information found in your documents." (threshold check)
6. **Check query history** — entries appear with timestamps and chunk counts
7. **Delete a document** — it disappears from the list; queries afterwards no longer use it
8. **Log out / log back in** — documents and history reload for the same user

### Multi-user isolation checks (API-level)

```bash
# Register two users, get tokens
TOKEN_A=$(curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"password123"}' >/dev/null; \
  curl -s -X POST http://localhost:8000/api/auth/login \
  -d "username=alice&password=password123" | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
# (repeat for bob, then:)

# Alice's documents are invisible to Bob
curl -s http://localhost:8000/api/documents/1 -H "Authorization: Bearer $TOKEN_B"   # → 404

# A query without document_ids only searches the caller's own chunks
curl -s -X POST http://localhost:8000/api/query \
  -H "Authorization: Bearer $TOKEN_B" -H "Content-Type: application/json" \
  -d '{"query_text": "anything"}'
```

The Swagger UI at http://localhost:8000/docs also works end-to-end — use the
`Authorize` button with `username`/`password` (it logs in via `/api/auth/login`).

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Login returns 500 | `JWT_SECRET` missing — set it in `.env` (compose provides a dev default) |
| Upload returns 502 | Gemini API key invalid/quota exhausted — check backend logs |
| Query always says "No relevant information" | Document chunks never crossed the 0.5 threshold; try quoting the document or re-upload |
| Schema errors after pulling new code | `docker compose down -v` to reset the dev database, then `up` |
| Frontend stuck on "API Disconnected" | Backend not up, or `VITE_API_BASE_URL` wrong; the badge polls every 30 s |
