# Ingatini: A Personal Knowledge Search Engine

A lightweight Retrieval-Augmented Generation (RAG) application for uploading documents and asking AI-powered questions about them. Built with FastAPI, LangChain, PostgreSQL, and Gemini.

## 🎯 Core Idea

1. User uploads documents (PDF, DOCX, TXT)
2. System extracts text and creates embeddings
3. Embeddings stored in PostgreSQL with pgvector
4. User asks questions via chat interface
5. RAG pipeline retrieves relevant chunks and augments LLM response

## 📋 Project Status

| Phase | Task | Status |
|-------|------|--------|
| 1 | Backend structure & DB schema | ✅ Complete |
| 2 | Embedding pipeline & document processing | ⏳ In Progress |
| 3 | RAG query engine & retrieval | ⏳ Next |
| 4 | Frontend UI (React/Vite) | ⏳ Next |
| 5 | Deployment & automation | 📅 Post-launch |

## 🚀 Quick Start

```bash
# Clone and setup
cd /home/fazrigading/Projects/ingatini

# Copy environment template
cp backend/.env.example backend/.env

# Start with Docker
docker-compose up

# Or use the helper script
./dev start
```

**API Documentation**: http://localhost:8000/docs  
**Health Check**: `curl http://localhost:8000/api/health`

See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed setup instructions.

## 🏗️ Architecture

### Backend
- **Framework**: FastAPI (Python)
- **ORM**: SQLAlchemy with PostgreSQL
- **Vector Storage**: pgvector (768-dim embeddings)
- **RAG Pipeline**: LangChain with Gemini
- **API**: RESTful with automatic docs

### Database
- **Users** — User accounts
- **Documents** — Document metadata
- **Chunks** — Text segments with embeddings
- **QueryLogs** — Query history for analytics

### Frontend (TODO)
- **Framework**: React/Vite
- **UI**: Clean, minimal interface
- **Features**: Document upload, chat with source attribution

## 📁 Project Structure

```
ingatini/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── core/        # Config & database
│   │   ├── api/         # Endpoints
│   │   ├── schemas/     # Pydantic models
│   │   ├── models/      # DB models
│   │   └── services/    # Business logic
│   ├── main.py
│   └── requirements.txt
├── frontend/            # React/Vite (TODO)
├── docker-compose.yml   # Dev environment
├── GETTING_STARTED.md   # Setup guide
├── IMPLEMENTATION.md    # Progress tracking
└── dev                  # Development helper
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
| **Embedding** | embedding-001 |
| **LLM** | gemini-pro |
| **Frontend** | React/Vite (TODO) |
| **Containerization** | Docker + Docker Compose |

## ⚙️ Configuration

Create `backend/.env` from `backend/.env.example`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/ingatini_db
GEMINI_API_KEY=your_key_here
GEMINI_EMBEDDING_MODEL=models/embedding-001
GEMINI_LLM_MODEL=gemini-pro
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