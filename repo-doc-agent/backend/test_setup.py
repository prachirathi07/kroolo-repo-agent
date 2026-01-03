"""
Test script to verify backend setup
Run this to check if all dependencies and configurations are correct
"""

import sys
import os

def test_imports():
    """Test if all required packages are installed"""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI installed")
    except ImportError:
        print("❌ FastAPI not installed")
        return False
    
    try:
        import langgraph
        print("✅ LangGraph installed")
    except ImportError:
        print("❌ LangGraph not installed")
        return False
    
    try:
        import groq
        print("✅ Groq SDK installed")
    except ImportError:
        print("❌ Groq SDK not installed")
        return False
    
    try:
        import git
        print("✅ GitPython installed")
    except ImportError:
        print("❌ GitPython not installed")
        return False
    
    try:
        import sqlalchemy
        print("✅ SQLAlchemy installed")
    except ImportError:
        print("❌ SQLAlchemy not installed")
        return False
    
    return True


def test_env_variables():
    """Test if environment variables are set"""
    print("\n🔍 Testing environment variables...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'GROQ_API_KEY',
        'DATABASE_URL',
        'SUPABASE_URL',
        'SUPABASE_KEY'
    ]
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value and value != f"your-{var.lower().replace('_', '-')}":
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is NOT set or using default value")
            all_set = False
    
    return all_set


def test_database_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        from app.core.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False


def test_groq_api():
    """Test Groq API connection"""
    print("\n🔍 Testing Groq API...")
    
    try:
        from app.services.llm_service import llm_service
        
        # Simple test
        response = llm_service._create_chat_completion([
            {"role": "user", "content": "Say 'Hello' in one word"}
        ])
        
        if response:
            print(f"✅ Groq API working. Response: {response[:50]}...")
            return True
        else:
            print("❌ Groq API returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Groq API test failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 RepoDocAgent Backend Setup Test")
    print("=" * 60)
    
    results = {
        "Imports": test_imports(),
        "Environment Variables": test_env_variables(),
        "Database Connection": test_database_connection(),
        "Groq API": test_groq_api()
    }
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! Backend is ready to use.")
        print("\nNext steps:")
        print("1. Run: uvicorn app.main:app --reload")
        print("2. Visit: http://localhost:8000/docs")
        print("3. Test with a repository!")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install missing packages: pip install -r requirements.txt")
        print("- Set environment variables in .env file")
        print("- Check database connection string")
        print("- Verify Groq API key")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
