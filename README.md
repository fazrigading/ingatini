# Ingatini: A Personal Knowledge Search Engine

A complete Retrieval-Augmented Generation (RAG) application for uploading documents and asking AI-powered questions about them. Full-stack implementation with FastAPI backend, React frontend, PostgreSQL database, and Google Gemini API.

## 🎯 Core Idea

1. User registers and uploads documents (PDF, DOCX, TXT)
2. System extracts text and creates embeddings via Gemini API
3. Embeddings stored in PostgreSQL with pgvector
4. User asks questions via React chat interface
5. RAG pipeline retrieves relevant chunks and augments Gemini response with context
6. Source attribution shows which documents contributed to each answer

## 📋 Project Status

| Phase | Task | Status |
|-------|------|--------|
| 1 | Backend structure & DB schema | ✅ Complete |
| 2 | Embedding pipeline & document processing | ✅ Complete |
| 3 | RAG query engine & retrieval | ✅ Complete |
| 4 | Frontend UI (React/Vite) | ✅ Complete |
| 5 | Authentication (Optional) | 📅 Future |

**Overall Progress:** 80% Complete (Full Stack MVP Ready)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend dev)
- GEMINI_API_KEY environment variable

### Run Full Stack

```bash
# 1. Start backend and database
docker compose up

# 2. In another terminal, start frontend
cd frontend
npm install  # (first time only)
npm run dev
```

**Backend API**: http://localhost:8000  
**API Docs**: http://localhost:8000/docs  
**Frontend App**: http://localhost:5173

See [END_TO_END_TESTING.md](END_TO_END_TESTING.md) for complete testing guide.

## 🏗️ Architecture

### Backend Stack
- **Framework**: FastAPI 0.109.0 (Python async)
- **Database**: PostgreSQL 15 + pgvector 0.2.4
- **ORM**: SQLAlchemy 2.0.23
- **AI**: Google Gemini API (embeddings + LLM)
- **RAG**: LangChain + custom pipeline
- **API**: RESTful with Swagger/OpenAPI docs

### Frontend Stack
- **Framework**: React 19.2.0
- **Build Tool**: Vite 7.3.1
- **Styling**: Tailwind CSS 4.x
- **HTTP Client**: Axios
- **State**: React hooks (useState, useEffect, useRef)

### Database Schema
- **Users** — User accounts & session management
- **Documents** — Document metadata, file info, chunk count
- **Chunks** — Text segments (512 chars, 50 char overlap) with 768-dim embeddings
- **QueryLogs** — Query history with responses, timing, source attribution

## 📁 Project Structure

```
ingatini/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py      # Settings from environment
│   │   │   └── database.py    # SQLAlchemy setup
│   │   ├── api/               # Endpoint handlers
│   │   │   ├── users.py
│   │   │   ├── documents.py
│   │   │   ├── query.py
│   │   │   └── health.py
│   │   ├── schemas/           # Pydantic models (request/response)
│   │   ├── models/            # SQLAlchemy ORM models
│   │   └── services/          # Business logic
│   │       ├── embedding_service.py    # Gemini embeddings
│   │       ├── rag_service.py          # RAG pipeline
│   │       ├── document_service.py
│   │       ├── document_parser.py      # PDF/DOCX/TXT extraction
│   │       └── text_processor.py       # Chunking & normalization
│   ├── main.py                # FastAPI app entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
│
├── frontend/                  # React + Vite app
│   ├── src/
│   │   ├── components/
│   │   │   ├── DocumentUpload.jsx     # File upload interface
│   │   │   ├── ChatInterface.jsx      # Chat & query interface
│   │   │   └── QueryHistory.jsx       # Past queries display
│   │   ├── services/
│   │   │   └── api.js                 # Axios API client
│   │   ├── App.jsx            # Main app component
│   │   ├── App.css
│   │   ├── index.css          # Global + Tailwind styles
│   │   └── main.jsx           # React entry point
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── .env.example
│   └── README.md
│
├── docker-compose.yml          # Development environment
├── .env                        # Environment variables (git ignored)
├── .env.example                # Environment template
│
├── Documentation/
│   ├── README.md              # This file
│   ├── GETTING_STARTED.md     # Setup & configuration guide
│   ├── STATUS.md              # Current completion status
│   ├── IMPLEMENTATION.md      # Detailed progress tracking
│   ├── COMPLETION_SUMMARY.md  # Phase-by-phase summary
│   ├── PHASE4_COMPLETION.md   # Frontend phase details
│   ├── END_TO_END_TESTING.md  # Complete testing guide
│   ├── QUICK_REF.sh           # Quick reference
│   └── FRONTEND_GUIDE.md      # Frontend setup guide
│
├── dev                        # Development CLI helper script
└── start.sh                   # Quick start script
```

## 🔧 Development

### Using Dev Helper

```bash
./dev start       # Start development
./dev logs        # View logs
./dev shell       # Access container
./dev test        # Run tests
./dev format      # Format code
```

### API Endpoints

```
POST   /api/users/                  # Create user
GET    /api/users/{id}              # Get user
POST   /api/documents/upload        # Upload document
GET    /api/documents/{user_id}     # List documents
POST   /api/query/                  # Query documents (RAG)
```

## 📚 Stack

| Layer | Technology |
|-------|-----------|
| **API** | FastAPI 0.109 |
| **Database** | PostgreSQL 15 + pgvector |
| **ORM** | SQLAlchemy 2.0 |
| **RAG** | LangChain + Gemini |
| **Embedding** | gemini-embedding-1.0 |
| **LLM** | gemini-3-flash |
| **Frontend** | React/Vite (TODO) |
| **Containerization** | Docker + Docker Compose |

## ⚙️ Configuration

Create `.env` from `.env.example`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/ingatini_db
GEMINI_API_KEY=your_key_here
GEMINI_EMBEDDING_MODEL=gemini-embedding-1.0
GEMINI_LLM_MODEL=gemini-3-flash
DEBUG=True
```

## 📖 Documentation

- [GETTING_STARTED.md](GETTING_STARTED.md) — Setup & usage guide
- [IMPLEMENTATION.md](IMPLEMENTATION.md) — Progress & architecture
- [backend/README.md](backend/README.md) — Backend development
- [frontend/README.md](frontend/README.md) — Frontend development

## 🛠️ Automation (Post-Development)

After MVP completion, integrate with n8n:
- Trigger: New file uploaded
- Action: Call embedding pipeline API
- Result: Auto-insert embeddings to database

## 📝 License

MIT

---

**Next**: See [GETTING_STARTED.md](GETTING_STARTED.md) to begin developing!