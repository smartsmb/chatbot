#!/usr/bin/env python3
"""
Example usage of the settings configuration system.

This demonstrates how the settings work with different environments:
- Default: SQLite for local development
- Override: PostgreSQL/RDS for production via environment variables
"""

import os
from settings import settings, get_settings

def example_default_configuration():
    """Example: Using default configuration (SQLite)."""
    print("=== Default Configuration (SQLite) ===")
    
    # Clear any existing environment variables
    for key in ["DATABASE_URL", "DB_HOST", "DB_PORT", "DB_NAME", "DB_USERNAME", "DB_PASSWORD"]:
        if key in os.environ:
            del os.environ[key]
    
    # Reload settings to get defaults
    from importlib import reload
    import settings
    reload(settings)
    default_settings = settings.settings
    
    print(f"Database URL: {default_settings.get_database_url()}")
    print(f"Database Type: {'SQLite' if default_settings.is_sqlite else 'PostgreSQL'}")
    print(f"Environment: {default_settings.ENVIRONMENT}")
    print(f"CORS Origins: {default_settings.CORS_ORIGINS}")
    print(f"Debug Mode: {default_settings.DEBUG}")
    print()

def example_production_configuration():
    """Example: Using production configuration (PostgreSQL/RDS)."""
    print("=== Production Configuration (PostgreSQL/RDS) ===")
    
    # Set production environment variables
    os.environ["DATABASE_URL"] = "postgresql+psycopg2://user:pass@rds.example.com:5432/chatbot"
    os.environ["ENVIRONMENT"] = "production"
    os.environ["JWT_SECRET"] = "super-secret-jwt-key-for-production"
    os.environ["CORS_ORIGINS"] = "https://myapp.com,https://www.myapp.com"
    os.environ["OPENAI_API_KEY"] = "sk-your-openai-key"
    os.environ["LOG_LEVEL"] = "WARNING"
    
    # Reload settings
    from importlib import reload
    import settings
    reload(settings)
    prod_settings = settings.settings
    
    print(f"Database URL: {prod_settings.get_database_url()}")
    print(f"Database Type: {'SQLite' if prod_settings.is_sqlite else 'PostgreSQL'}")
    print(f"Environment: {prod_settings.ENVIRONMENT}")
    print(f"CORS Origins: {prod_settings.CORS_ORIGINS}")
    print(f"Debug Mode: {prod_settings.DEBUG}")
    print(f"Log Level: {prod_settings.LOG_LEVEL}")
    print()

def example_database_components():
    """Example: Using database components instead of full URL."""
    print("=== Database Components Configuration ===")
    
    # Set database components
    os.environ["DB_HOST"] = "my-rds-instance.region.rds.amazonaws.com"
    os.environ["DB_PORT"] = "5432"
    os.environ["DB_NAME"] = "chatbot_prod"
    os.environ["DB_USERNAME"] = "admin"
    os.environ["DB_PASSWORD"] = "secure_password"
    os.environ["DATABASE_URL"] = ""  # Clear to test component construction
    
    # Reload settings
    from importlib import reload
    import settings
    reload(settings)
    comp_settings = settings.settings
    
    print(f"Database URL: {comp_settings.get_database_url()}")
    print(f"Database Type: {'SQLite' if comp_settings.is_sqlite else 'PostgreSQL'}")
    print(f"Host: {comp_settings.DB_HOST}")
    print(f"Port: {comp_settings.DB_PORT}")
    print(f"Database: {comp_settings.DB_NAME}")
    print()

def example_kubernetes_environment():
    """Example: Kubernetes environment variables."""
    print("=== Kubernetes Environment ===")
    
    # Simulate Kubernetes environment variables
    os.environ["ENVIRONMENT"] = "production"
    os.environ["DATABASE_URL"] = "postgresql+psycopg2://user:pass@postgres-service:5432/chatbot"
    os.environ["JWT_SECRET"] = "k8s-jwt-secret"
    os.environ["OPENAI_API_KEY"] = "sk-k8s-openai-key"
    os.environ["CORS_ORIGINS"] = "https://myapp.example.com"
    os.environ["LOG_LEVEL"] = "INFO"
    os.environ["DEBUG"] = "false"
    
    # Reload settings
    from importlib import reload
    import settings
    reload(settings)
    k8s_settings = settings.settings
    
    print(f"Environment: {k8s_settings.ENVIRONMENT}")
    print(f"Database URL: {k8s_settings.get_database_url()}")
    print(f"Database Type: {'SQLite' if k8s_settings.is_sqlite else 'PostgreSQL'}")
    print(f"CORS Origins: {k8s_settings.CORS_ORIGINS}")
    print(f"Debug Mode: {k8s_settings.DEBUG}")
    print(f"Log Level: {k8s_settings.LOG_LEVEL}")
    
    # Validate configuration
    issues = k8s_settings.validate_config()
    if issues:
        print(f"Configuration Issues: {issues}")
    else:
        print("✅ Configuration is valid!")
    print()

def example_validation():
    """Example: Configuration validation."""
    print("=== Configuration Validation ===")
    
    # Test with problematic configuration
    os.environ["ENVIRONMENT"] = "production"
    os.environ["JWT_SECRET"] = "your-secret-key-change-in-production"  # Default secret
    os.environ["OPENAI_API_KEY"] = ""  # Missing API key
    os.environ["DATABASE_URL"] = "sqlite:///./chatbot.db"  # SQLite in production
    
    # Reload settings
    from importlib import reload
    import settings
    reload(settings)
    test_settings = settings.settings
    
    issues = test_settings.validate_config()
    print(f"Configuration Issues: {issues}")
    print()

def main():
    """Run all examples."""
    print("🔧 Settings Configuration Examples\n")
    
    example_default_configuration()
    example_production_configuration()
    example_database_components()
    example_kubernetes_environment()
    example_validation()
    
    print("📚 Usage Summary:")
    print("1. Default: SQLite database, development settings")
    print("2. Environment Variables: Override any setting")
    print("3. Database Components: Build PostgreSQL URL from parts")
    print("4. Kubernetes: Use ConfigMaps and Secrets")
    print("5. Validation: Check configuration before deployment")

if __name__ == "__main__":
    main()
