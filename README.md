# AI Chatbot Application

A full-stack chatbot application built with FastAPI backend, React frontend, and Docker containerization.

## Features

- **Backend (FastAPI)**

  - JWT-based authentication
  - SQLite database with SQLAlchemy ORM
  - OpenAI GPT integration
  - RESTful API with automatic documentation
  - User registration and login
  - Conversation management
  - Message history

- **Frontend (React + Vite)**

  - Modern React with hooks
  - Responsive design
  - Real-time chat interface
  - User authentication
  - Conversation sidebar
  - Message history

- **Docker**
  - Multi-container setup with docker-compose
  - Development environment with hot reload
  - Easy deployment

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Colima (for macOS) or Docker Desktop

### 1. Start Colima & Set Context

```bash
colima start
docker context use colima
```

### 2. Set Up Environment Variables

```bash
# Copy environment files
cp backend/env.example backend/.env
cp frontend/env.example frontend/.env

# Edit backend/.env and add your secrets:
# OPENAI_API_KEY=<your_openai_api_key>
# JWT_SECRET=your_jwt_secret_here_change_this_in_production
```

### 3. Run with Docker

```bash
# Set environment variables and start services
OPENAI_API_KEY=<your_openai_api_key> JWT_SECRET=change-me docker-compose up --build
```

### 4. Access the Application

- **Web UI**: [http://localhost:5173](http://localhost:5173)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Authentication

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user info

### Conversations

- `GET /conversations` - Get user's conversations
- `POST /conversations` - Create new conversation
- `GET /conversations/{id}` - Get specific conversation

### Chat

- `POST /chat` - Send message to AI

## Project Structure

```
chatbot/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database models and connection
│   ├── auth.py              # JWT authentication
│   ├── models.py            # Pydantic models
│   ├── openai_client.py     # OpenAI integration
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile          # Backend container
│   └── env.example         # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── contexts/        # React contexts
│   │   ├── services/        # API services
│   │   └── App.jsx         # Main app component
│   ├── package.json        # Node dependencies
│   ├── Dockerfile         # Frontend container
│   └── env.example        # Environment variables template
├── docker-compose.yml     # Multi-container setup
└── README.md             # This file
```

## Environment Variables

### Backend (.env)

```
OPENAI_API_KEY=your_openai_api_key_here
JWT_SECRET=your_jwt_secret_here_change_this_in_production
DATABASE_URL=sqlite:///./chatbot.db
```

### Frontend (.env)

```
VITE_API_URL=http://localhost:8000
```

## Database

The application uses SQLite for development. The database file (`chatbot.db`) will be created automatically when you first run the application.

### Database Schema

- **Users**: User accounts with authentication
- **Conversations**: Chat conversations
- **Messages**: Individual messages in conversations

## Security

- JWT tokens for authentication
- Password hashing with bcrypt
- CORS configured for frontend
- Input validation with Pydantic

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

