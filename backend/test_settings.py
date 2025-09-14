#!/usr/bin/env python3
"""
Test script to verify settings configuration works correctly.
"""

import os
import sys
from settings import settings, get_settings

def test_default_configuration():
    """Test that default configuration works (SQLite)."""
    print("Testing default configuration (SQLite)...")
    
    # Test default values
    assert settings.DATABASE_URL == "sqlite:///./chatbot.db", f"Expected SQLite URL, got {settings.DATABASE_URL}"
    assert settings.is_sqlite == True, "Should be using SQLite"
    assert settings.is_postgresql == False, "Should not be using PostgreSQL"
    assert settings.ENVIRONMENT == "development", f"Expected development, got {settings.ENVIRONMENT}"
    assert any("localhost" in origin for origin in settings.CORS_ORIGINS), "Should include localhost in CORS origins"
    
    print("✅ Default configuration test passed!")

def test_environment_override():
    """Test that environment variables override defaults."""
    print("Testing environment variable override...")
    
    # Set test environment variables
    os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/testdb"
    os.environ["ENVIRONMENT"] = "production"
    os.environ["JWT_SECRET"] = "test-secret-key"
    os.environ["CORS_ORIGINS"] = "https://example.com,https://app.example.com"
    
    # Reload settings
    from importlib import reload
    import settings
    reload(settings)
    test_settings = settings.settings
    
    # Test overrides
    assert test_settings.DATABASE_URL == "postgresql://user:pass@localhost:5432/testdb", f"Expected PostgreSQL URL, got {test_settings.DATABASE_URL}"
    assert test_settings.is_postgresql == True, "Should be using PostgreSQL"
    assert test_settings.is_sqlite == False, "Should not be using SQLite"
    assert test_settings.ENVIRONMENT == "production", f"Expected production, got {test_settings.ENVIRONMENT}"
    assert "https://example.com" in test_settings.CORS_ORIGINS, "Should include example.com in CORS origins"
    
    print("✅ Environment override test passed!")

def test_database_url_construction():
    """Test database URL construction from components."""
    print("Testing database URL construction...")
    
    # Set database components
    os.environ["DB_HOST"] = "rds.example.com"
    os.environ["DB_PORT"] = "5432"
    os.environ["DB_NAME"] = "chatbot"
    os.environ["DB_USERNAME"] = "admin"
    os.environ["DB_PASSWORD"] = "secret"
    os.environ["DATABASE_URL"] = ""  # Clear to test construction
    
    # Reload settings
    from importlib import reload
    import settings
    reload(settings)
    test_settings = settings.settings
    
    # Test URL construction
    constructed_url = test_settings.get_database_url()
    expected_url = "postgresql+psycopg2://admin:secret@rds.example.com:5432/chatbot"
    assert constructed_url == expected_url, f"Expected {expected_url}, got {constructed_url}"
    
    print("✅ Database URL construction test passed!")

def test_configuration_validation():
    """Test configuration validation."""
    print("Testing configuration validation...")
    
    # Test with missing OpenAI key
    os.environ["OPENAI_API_KEY"] = ""
    os.environ["JWT_SECRET"] = "your-secret-key-change-in-production"
    os.environ["ENVIRONMENT"] = "production"
    
    # Reload settings
    from importlib import reload
    import settings
    reload(settings)
    test_settings = settings.settings
    
    issues = test_settings.validate_config()
    assert len(issues) > 0, "Should have validation issues"
    assert any("OPENAI_API_KEY" in issue for issue in issues), "Should flag missing OpenAI key"
    assert any("JWT_SECRET" in issue for issue in issues), "Should flag default JWT secret in production"
    
    print("✅ Configuration validation test passed!")

def test_sqlite_fallback():
    """Test SQLite fallback when PostgreSQL components are missing."""
    print("Testing SQLite fallback...")
    
    # Clear all database-related environment variables
    for key in ["DATABASE_URL", "DB_HOST", "DB_PORT", "DB_NAME", "DB_USERNAME", "DB_PASSWORD"]:
        if key in os.environ:
            del os.environ[key]
    
    # Reload settings
    from importlib import reload
    import settings
    reload(settings)
    test_settings = settings.settings
    
    # Should fallback to SQLite
    assert test_settings.get_database_url() == "sqlite:///./chatbot.db", "Should fallback to SQLite"
    assert test_settings.is_sqlite == True, "Should be using SQLite"
    
    print("✅ SQLite fallback test passed!")

def main():
    """Run all tests."""
    print("🧪 Testing Settings Configuration\n")
    
    try:
        test_default_configuration()
        test_environment_override()
        test_database_url_construction()
        test_configuration_validation()
        test_sqlite_fallback()
        
        print("\n🎉 All tests passed! Settings configuration is working correctly.")
        print(f"\nCurrent configuration:\n{settings}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
