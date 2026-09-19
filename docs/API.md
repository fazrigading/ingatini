# API Reference

Base URL: `http://localhost:8000/api` (dev). Interactive docs: `http://localhost:8000/docs`.

All endpoints except `/health` and the auth endpoints require a Bearer token:

```
Authorization: Bearer <access_token>
```

A `401` response means the token is missing, invalid, or expired.

---

## Health

### `GET /health`

Verifies service and database connectivity. No auth required.

```json
{ "status": "ok", "service": "ingatini-api", "database": "ok" }
```

---

## Auth

### `POST /auth/register`

Create an account. Passwords must be at least 8 characters.

```json
{ "username": "john_doe", "email": "john@example.com", "password": "s3cret-pass" }
```

**201** returns the user:

```json
{ "id": 1, "username": "john_doe", "email": "john@example.com", "created_at": "...", "updated_at": "..." }
```

**400** if the email or username is already taken.

### `POST /auth/login`

Authenticate. Accepts `application/x-www-form-urlencoded` (OAuth2 password form):

```
username=john_doe&password=s3cret-pass
```

**200** returns a JWT and the user:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": { "id": 1, "username": "john_doe", "email": "john@example.com" }
}
```

**401** for incorrect credentials.

### `GET /auth/me`

Returns the authenticated user (same shape as above).

---

## Documents

Owned by the authenticated user; other users' documents are invisible.

### `POST /documents/upload`

Upload and process a document through the RAG pipeline (extract → chunk → embed). Multipart form with a `file` field.

- Allowed: `.pdf`, `.docx`, `.txt`
- Max size: 10 MB

**200** returns:

```json
{ "id": 1, "filename": "report.pdf", "total_chunks": 42, "message": "Document processed successfully with 42 chunks" }
```

**400** unsupported format, **413** too large, **502** embedding service unavailable.

### `GET /documents`

List the authenticated user's documents.

**200** returns an array of documents:

```json
[
  {
    "id": 1, "user_id": 1, "filename": "report.pdf", "file_size": 102400,
    "content_type": "application/pdf", "total_chunks": 42,
    "created_at": "...", "updated_at": "..."
  }
]
```

### `GET /documents/{doc_id}`

Get a single owned document. **404** if it doesn't exist or belongs to another user.

### `DELETE /documents/{doc_id}`

Delete an owned document and its chunks. **404** if not found or not owned. Returns `{ "message": "Document deleted successfully" }`.

---

## Query (RAG)

### `POST /query`

Ask a question against the authenticated user's documents.

```json
{
  "query_text": "What is the main topic?",
  "document_ids": [1, 2],
  "top_k": 5
}
```

- `document_ids` (optional): narrow the search to specific owned documents
- `top_k` (optional, 1–20, default 5): how many chunks to retrieve

**200** returns:

```json
{
  "query_text": "What is the main topic?",
  "response": "The document discusses ...",
  "retrieved_chunks": [
    {
      "id": 17, "document_id": 1, "chunk_index": 3,
      "content": "...", "token_count": 256, "similarity": 0.6412
    }
  ],
  "response_time_ms": 2310.45
}
```

If nothing clears the similarity threshold (0.5), `response` is "No relevant information found in your documents." and `retrieved_chunks` is empty.

**502** if the embedding or LLM service is unavailable.

### `GET /query/history?limit=10`

Query history for the authenticated user (most recent first, `limit` capped at 100).

```json
{
  "user_id": 1,
  "history": [
    {
      "id": 9,
      "query": "What is the main topic?",
      "response": "The document discusses ...",
      "chunks_count": 5,
      "created_at": "2026-09-20T02:11:22"
    }
  ]
}
```
