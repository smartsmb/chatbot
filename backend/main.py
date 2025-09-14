from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, create_tables, User, Conversation, Message
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from models import UserCreate, UserResponse, UserLogin, Token, ChatRequest, ChatResponse, ConversationResponse, MessageResponse
from openai_client import openai_client
from settings import settings
from datetime import timedelta
import asyncio

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# CORS middleware with settings-driven configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
create_tables()

@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/conversations", response_model=list[ConversationResponse])
async def get_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversations = db.query(Conversation).filter(Conversation.user_id == current_user.id).order_by(Conversation.updated_at.desc()).all()
    return conversations

@app.post("/conversations", response_model=ConversationResponse)
async def create_conversation(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = Conversation(user_id=current_user.id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

@app.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get or create conversation
    if request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(user_id=current_user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    # Get conversation history for context
    messages = db.query(Message).filter(Message.conversation_id == conversation.id).order_by(Message.created_at).all()
    
    # Prepare messages for OpenAI
    openai_messages = []
    for msg in messages:
        openai_messages.append({
            "role": msg.role,
            "content": msg.content
        })
    
    # Generate AI response
    ai_response = await openai_client.generate_response(openai_messages)
    
    # Save AI response
    ai_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=ai_response
    )
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)
    
    # Update conversation title if it's the first message
    if len(messages) == 1:
        conversation.title = request.message[:50] + "..." if len(request.message) > 50 else request.message
        db.commit()
    
    return ChatResponse(
        message=ai_response,
        conversation_id=conversation.id,
        message_id=ai_message.id
    )

@app.get("/")
async def root():
    return {"message": "Chatbot API is running!"}

@app.get("/health")
async def health_check():
    """Health check endpoint with configuration validation."""
    issues = settings.validate_config()
    return {
        "status": "healthy" if not issues else "unhealthy",
        "environment": settings.ENVIRONMENT,
        "database": "SQLite" if settings.is_sqlite else "PostgreSQL",
        "issues": issues
    }

@app.get("/config")
async def get_config():
    """Get current configuration (excluding sensitive data)."""
    return {
        "environment": settings.ENVIRONMENT,
        "database_type": "SQLite" if settings.is_sqlite else "PostgreSQL",
        "debug": settings.DEBUG,
        "log_level": settings.LOG_LEVEL,
        "cors_origins": settings.CORS_ORIGINS,
        "openai_model": settings.OPENAI_MODEL,
        "token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)



