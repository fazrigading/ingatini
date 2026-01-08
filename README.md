# Ingatini: A Personal Knowledge Search Engine
A small project for learning how to develop Light RAG app

## Core Idea
- An user uploads documents
- The system extracts text, embeds it, stores metadata in Postgres, and provides a simple retrieval-augmented Q&A interface

## Back-end Plan
- **Endpoints**: Document upload, embedding pipeline, query endpoint.
- Lightweight RAG pipeline using LangChain (text splitter -> embeddings -> retrieval -> LLM call).
- Store embeddings in Postgres using a vector extension alternative (approx. numeric fields or pgvector-lite, depending on hosting).

## Front-end plan
- Document upload UI
- Simple chat interface that shows sources of the information
- Results dislayed with minimal style

## Database
- Only Postgres
- One table for chunks, one for metadata, and one for userdata.

## Automation (Post-develop stage)
- Use n8n to automate
- When new file uploaded -> Call API -> Run embedding -> insert to DB
<!-- Daily cleanup? -->

## MLOps
- No tracking, model config stored in code
- Use free hosting for backend & frontend.