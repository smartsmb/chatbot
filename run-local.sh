#!/bin/bash

# Run local development environment
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting local development environment${NC}"

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}Creating backend/.env file...${NC}"
    cat > backend/.env << EOF
# Local Development Environment
DATABASE_URL=sqlite:///./chatbot.db
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
LOG_LEVEL=DEBUG
OPENAI_API_KEY=your-openai-key-here
JWT_SECRET=local-dev-secret
EOF
    echo -e "${YELLOW}Please update backend/.env with your actual OpenAI API key${NC}"
fi

if [ ! -f "frontend/.env" ]; then
    echo -e "${YELLOW}Creating frontend/.env file...${NC}"
    cat > frontend/.env << EOF
# Local Development Environment
VITE_API_URL=http://localhost:8000
EOF
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Start services
echo -e "${YELLOW}Starting services with docker-compose...${NC}"
docker-compose -f docker-compose.local.yml up --build

echo -e "${GREEN}Local development environment started!${NC}"
echo -e "${YELLOW}Backend: http://localhost:8000${NC}"
echo -e "${YELLOW}Frontend: http://localhost:5173${NC}"
echo -e "${YELLOW}API Docs: http://localhost:8000/docs${NC}"
