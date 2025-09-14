#!/bin/bash

# AI Chatbot - Quick Start Script

echo "🤖 AI Chatbot Setup"
echo "==================="

# Check if Colima is running
if ! docker context ls | grep -q "colima"; then
    echo "❌ Colima context not found. Please run:"
    echo "   colima start"
    echo "   docker context use colima"
    exit 1
fi

# Check if environment files exist
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating backend environment file..."
    cp backend/env.example backend/.env
    echo "⚠️  Please edit backend/.env and add your OPENAI_API_KEY and JWT_SECRET"
fi

if [ ! -f "frontend/.env" ]; then
    echo "📝 Creating frontend environment file..."
    cp frontend/env.example frontend/.env
fi

# Check if required environment variables are set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set. Using value from backend/.env"
fi

if [ -z "$JWT_SECRET" ]; then
    echo "⚠️  JWT_SECRET not set. Using default value"
    export JWT_SECRET="change-me-in-production"
fi

echo "🚀 Starting services with Docker Compose..."
echo "   Web UI: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
echo ""

docker-compose up --build
