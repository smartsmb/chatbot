"""
Settings configuration for the Chatbot API.

This module provides environment-driven configuration with safe defaults:
- Default: SQLite database for local development
- Override: Environment variables for production/K8s deployments

Configuration Priority:
1. Environment variables (highest priority)
2. Default values (fallback)
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def _parse_cors_origins(cors_origins: str) -> List[str]:
    """Parse CORS origins from comma-separated string."""
    if not cors_origins:
        return ["http://localhost:5173"]
    
    origins = [origin.strip() for origin in cors_origins.split(",")]
    return [origin for origin in origins if origin]


class Settings:
    """Application settings with environment-driven configuration."""
    
    # Application settings
    APP_NAME: str = "Chatbot API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database configuration
    # Default: SQLite for local development (safe default)
    # Override: PostgreSQL/RDS for production via DATABASE_URL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./chatbot.db")
    
    # Database connection details (for PostgreSQL)
    DB_HOST: Optional[str] = os.getenv("DB_HOST")
    DB_PORT: Optional[str] = os.getenv("DB_PORT")
    DB_NAME: Optional[str] = os.getenv("DB_NAME")
    DB_USERNAME: Optional[str] = os.getenv("DB_USERNAME")
    DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD")
    
    # Security settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    # CORS settings
    CORS_ORIGINS: List[str] = _parse_cors_origins(os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"))
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Database connection arguments
    @property
    def database_connect_args(self) -> dict:
        """Get database connection arguments based on database type."""
        if "sqlite" in self.DATABASE_URL:
            return {"check_same_thread": False}
        return {}
    
    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return "sqlite" in self.DATABASE_URL
    
    @property
    def is_postgresql(self) -> bool:
        """Check if using PostgreSQL database."""
        return "postgresql" in self.DATABASE_URL or "postgres" in self.DATABASE_URL
    
    def get_database_url(self) -> str:
        """Get the database URL, constructing it from components if needed."""
        if self.DATABASE_URL and self.DATABASE_URL != "sqlite:///./chatbot.db":
            return self.DATABASE_URL
        
        # If using PostgreSQL components, construct the URL
        if self.DB_HOST and self.DB_NAME:
            username = self.DB_USERNAME or "postgres"
            password = self.DB_PASSWORD or ""
            port = self.DB_PORT or "5432"
            
            if password:
                return f"postgresql+psycopg2://{username}:{password}@{self.DB_HOST}:{port}/{self.DB_NAME}"
            else:
                return f"postgresql+psycopg2://{username}@{self.DB_HOST}:{port}/{self.DB_NAME}"
        
        # Fallback to SQLite
        return "sqlite:///./chatbot.db"
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return any issues."""
        issues = []
        
        # Check required settings
        if not self.OPENAI_API_KEY:
            issues.append("OPENAI_API_KEY is required")
        
        # Check JWT secret for production
        if self.ENVIRONMENT == "production" and self.JWT_SECRET == "your-secret-key-change-in-production":
            issues.append("JWT_SECRET must be changed for production")
        
        # Check database configuration for production
        if self.ENVIRONMENT == "production" and self.is_sqlite:
            issues.append("SQLite is not recommended for production. Consider using PostgreSQL/RDS")
        
        return issues
    
    def __str__(self) -> str:
        """String representation of settings (excluding sensitive data)."""
        return f"""
Settings:
  Environment: {self.ENVIRONMENT}
  Database: {'SQLite' if self.is_sqlite else 'PostgreSQL'}
  Database URL: {self.DATABASE_URL[:50] + '...' if len(self.DATABASE_URL) > 50 else self.DATABASE_URL}
  Debug: {self.DEBUG}
  Log Level: {self.LOG_LEVEL}
  CORS Origins: {', '.join(self.CORS_ORIGINS[:3])}{'...' if len(self.CORS_ORIGINS) > 3 else ''}
"""


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


# Validate configuration on import
if __name__ == "__main__":
    issues = settings.validate_config()
    if issues:
        print("Configuration Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Configuration is valid!")
        print(settings)
