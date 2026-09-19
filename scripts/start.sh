#!/bin/bash
# Quick start script for local development

# Always operate from the repo root (compose file lives there)
cd "$(dirname "$0")/.."

echo "🚀 Ingatini Setup Script"
echo "========================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed."

# Setup .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your Gemini API key"
fi

# Start services
echo "🐳 Starting Docker services..."
docker compose up --build

echo "✅ Services are running!"
echo ""
echo "📖 API Documentation: http://localhost:8000/docs"
echo "💻 Health Check: curl http://localhost:8000/api/health"
