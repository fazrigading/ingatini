"""Python project README with development guide."""
# Ingatini Backend

Light RAG application backend built with FastAPI, LangChain, and PostgreSQL.

## Quick Start

### 1. Setup Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

### 3. Run with Docker Compose

```bash
# From project root
docker-compose up
```

Or run locally:

```bash
# Setup PostgreSQL first
# Then run the app
uvicorn main:app --reload
```

## Project Structure

```
backend/
├── app/
│   ├── core/          # Configuration & database setup
│   ├── api/           # API routes & endpoints
│   ├── schemas/       # Pydantic models for validation
│   ├── services/      # Business logic & RAG pipeline
│   └── models/        # SQLAlchemy database models
├── main.py            # FastAPI application entry point
├── requirements.txt   # Python dependencies
└── Dockerfile         # Container configuration
```

## API Documentation

Once running, visit: `http://localhost:8000/docs`

## Next Steps

- [ ] Create database models for documents, chunks, and embeddings
- [ ] Implement document upload and text extraction
- [ ] Build embedding pipeline with LangChain
- [ ] Create RAG query endpoint
- [ ] Add authentication/authorization
