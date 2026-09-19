# Ingatini Frontend

React 19 + Vite 7 + Tailwind CSS 4 client for the Ingatini RAG app.

## Features

- **Login / register** — JWT session persisted in `localStorage`, attached to
  every request by an Axios interceptor; a 401 clears the session
- **Document upload** — PDF, DOCX, TXT (10 MB limit enforced server-side)
- **Chat Q&A** — answers with per-source similarity scores
- **Document list with delete**
- **Query history** — past questions, answers, chunk counts
- **API status badge** — polls health every 30 s

## Setup

```bash
cd frontend
npm install
cp .env.example .env    # set VITE_API_BASE_URL if backend isn't on :8000
npm run dev             # http://localhost:5173
```

Backend must be running (see [backend README](../backend/README.md)).

## Commands

```bash
npm run dev        # dev server with HMR
npm run build      # production build → dist/
npm run preview    # serve the production build
npm run lint
```

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000/api` | Backend API URL (baked in at build time) |

## Structure

```
src/
├── components/
│   ├── DocumentUpload.jsx      # File picker + upload status
│   ├── ChatInterface.jsx       # Q&A with sources
│   └── QueryHistory.jsx        # Past queries
├── services/api.js             # Axios instance, token storage, interceptors
├── App.jsx                     # Auth state, layout, document list
└── index.css                   # Tailwind 4 entry (@import "tailwindcss")
```

### Auth flow

`api.js` stores the JWT under the `ingatini_token` localStorage key, attaches
`Authorization: Bearer <token>` on every call, and a response interceptor
wipes it on 401 so `App.jsx` falls back to the login form. Backend identity is
token-derived — no `user_id` is ever sent by the client.

## Troubleshooting

**API connection errors** — backend down? (`docker compose up`) · wrong
`VITE_API_BASE_URL`? · CORS errors in the browser console (check backend
`CORS_ORIGINS`)?

**401 loop after login** — `JWT_SECRET` changed server-side; log out, clear
`ingatini_token` from localStorage, log in again.

**Build issues**
```bash
rm -rf node_modules/.vite && npm install   # clear Vite cache
```

**Port 5173 busy** — `npm run dev -- --port 5174`
