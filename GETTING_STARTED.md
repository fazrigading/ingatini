<!--
GETTING STARTED - Ingatini RAG Application
Complete guide for setting up and running the project
-->

# 🚀 Getting Started with Ingatini

## Overview

Ingatini is a lightweight Retrieval-Augmented Generation (RAG) application that allows users to upload documents and ask questions about them using AI.

**Current Status**: Phase 4 ✅ Complete Full-Stack Application (Backend + Frontend)

---

## Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for local backend development)
- Gemini API key
- Git

---

## Quick Start (Docker - Recommended)

### 1. Clone and Setup

```bash
cd ingatini/

# Copy environment template
cp .env.example .env

# Edit .env and add your Gemini API key
nano .env  # or your favorite editor
```

### 2. Start Backend Services

```bash
# Option A: Using our dev helper
./dev start

# Option B: Using Docker Compose V2
docker compose up

# Option C: Using the shell script
bash start.sh
```

### 3. Start Frontend (in another terminal)

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

### 4. Access the Application

```
Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs
Frontend App: http://localhost:5173
```

---

## Local Development (Without Docker)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys
```

### 2. Database Setup

You'll need PostgreSQL with pgvector extension running:

```bash
# Using Docker for just the database
docker run -d \
  --name ingatini_postgres \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=ingatini_db \
  -p 5432:5432 \
  pgvector/pgvector:pg15
```

### 3. Run Backend

```bash
# From backend directory
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

---

## Development Commands

### Using the Dev Helper

```bash
# View all commands
./dev

# Common commands
./dev start       # Start development server
./dev stop        # Stop all containers
./dev rebuild     # Rebuild and restart
./dev logs        # View live logs
./dev shell       # Access backend bash shell
./dev test        # Run tests
./dev format      # Format code (black, isort)
./dev lint        # Lint code (flake8)
```

### Frontend Development Commands

```bash
cd frontend

# Start dev server with HMR
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Format code
npm run format
```

### Manual Docker Commands

```bash
# Start services
docker compose up --build

# View logs
docker compose logs -f backend

# Access backend shell
docker compose exec backend bash

# Stop services
docker compose down

# Clean up everything
docker compose down -v
```

---

## Project Structure

```
ingatini/
├── backend/                   # FastAPI backend
│   ├── app/
│   │   ├── core/              # Config & database
│   │   ├── api/               # Route handlers
│   │   ├── schemas/           # Pydantic models
│   │   ├── models/            # Database models
│   │   └── services/          # Business logic
│   ├── main.py                # Entry point
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── README.md
│
├── frontend/                  # React/Vite frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API client
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── .env.example
│   ├── README.md
│   └── dist/                  # Build output
│
├── docker-compose.yml         # Dev environment
├── GETTING_STARTED.md         # Setup guide
├── IMPLEMENTATION.md          # Progress tracking
├── README.md                  # Project overview
└── dev                        # Development helper script
```

---

## API Endpoints

### Health Check
```bash
GET /api/health
```

### Users
```bash
# Create user
POST /api/users/
{
  "username": "john_doe",
  "email": "john@example.com"
}

# Get user
GET /api/users/{user_id}

# List users
GET /api/users/?skip=0&limit=10
```

### Documents
```bash
# Upload document
POST /api/documents/upload?user_id=1
Content-Type: multipart/form-data
[file content]

# List documents
GET /api/documents/{user_id}

# Get document
GET /api/documents/{doc_id}

# Delete document
DELETE /api/documents/{doc_id}
```

### Query (RAG)
```bash
# Query documents
POST /api/query/
{
  "user_id": 1,
  "query_text": "What is the main topic?"
}

# Get query history
GET /api/query/history/{user_id}
```

---

## Environment Variables

Key configuration in `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ingatini_db

# Gemini API
GEMINI_API_KEY=your_key_here
GEMINI_EMBEDDING_MODEL=models/gemini-embedding-1.0
GEMINI_LLM_MODEL=gemini-3-flash

# Application
DEBUG=True
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Server
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

---

## Testing the Application

### End-to-End Workflow

1. **Create User**
   ```bash
   curl -X POST http://localhost:8000/api/users/ \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com"}'
   ```

2. **Upload Document** (via Frontend)
   - Go to http://localhost:5173
   - Click "Upload Document"
   - Select PDF, DOCX, or TXT file
   - Wait for processing

3. **Ask Question** (via Frontend)
   - Type question in chat interface
   - View answer with source attribution
   - Check query history

### Using Swagger UI

Visit `http://localhost:8000/docs` to interact with the API through the web interface.

---

## Next Steps

- [x] **Phase 1**: Backend structure & database
- [x] **Phase 2**: Embedding pipeline
- [x] **Phase 3**: RAG query engine
- [x] **Phase 4**: Frontend application
- [ ] **Phase 5**: Authentication (optional)
- [ ] **Phase 6**: Deploy to production

See `IMPLEMENTATION.md` for detailed progress tracking.

---

## Troubleshooting

### Docker Issues

```bash
# Containers won't start
docker compose down -v
docker compose up --build

# Permission denied
sudo chmod +x dev start.sh

# Port already in use
docker compose down
```

### Frontend Issues

```bash
# Modules not found
cd frontend
npm install

# Port 5173 in use
npm run dev -- --port 5174
```

### Database Issues

```bash
# Connect to database
docker compose exec postgres psql -U user -d ingatini_db

# Check tables
\dt

# View pgvector extension
\dx
```

### API Issues

```bash
# View backend logs
docker compose logs backend

# Restart backend
docker compose restart backend

# Full rebuild
docker compose up --build --force-recreate
```

---

## Configuration Tips

### Use Local LLM (Ollama)

To avoid Gemini costs, use Ollama for local embeddings:

1. Install [Ollama](https://ollama.ai)
2. Pull model: `ollama pull mistral`
3. Update `requirements.txt` to use LangChain's local embeddings
4. Set `GEMINI_API_KEY` to empty string

### Database Persistence

PostgreSQL data is stored in a Docker volume (`postgres_data`). To clear:

```bash
docker compose down -v
```

### CORS Configuration

Frontend and backend run on different ports. CORS origins are configured in `.env`:

```env
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [LangChain Documentation](https://python.langchain.com/)
- [PostgreSQL pgvector](https://github.com/pgvector/pgvector)
- [Gemini API Reference](https://ai.google.dev/docs)

---

## Contributing

See individual component README files:
- `backend/README.md` : Backend development
- `frontend/README.md` : Frontend development
- `IMPLEMENTATION.md` : Progress and architecture

---

## License

MIT
