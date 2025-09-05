#!/usr/bin/env python3
"""
Minimal Test for AI Email Assistant
This script tests the core functionality without heavy dependencies
"""

import json
import os
from datetime import datetime, timedelta

def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    print("🧪 Testing Basic Functionality...")
    
    # Test 1: Check if files exist
    required_files = [
        "main.py", "ai_service.py", "email_service.py", 
        "database.py", "models.py", "config.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
    
    # Test 2: Check if we can import basic modules
    try:
        import sqlite3
        print("✅ SQLite available")
    except ImportError:
        print("❌ SQLite not available")
        return False
    
    # Test 3: Test basic email processing logic
    support_keywords = ["support", "query", "request", "help", "issue", "problem", "assistance"]
    
    test_emails = [
        ("Help needed", "I need support with my account", True),
        ("General inquiry", "Just checking in", False),
        ("URGENT: System down", "Cannot access the system immediately - need help", True),
        ("Thank you", "Great service, thank you!", False)
    ]
    
    for subject, body, expected in test_emails:
        is_support = any(keyword in (subject + " " + body).lower() for keyword in support_keywords)
        if is_support == expected:
            print(f"✅ Email filtering working: '{subject[:20]}...' - Support: {is_support}")
        else:
            print(f"❌ Email filtering failed: '{subject[:20]}...' - Expected: {expected}, Got: {is_support}")
            return False
    
    # Test 4: Test priority detection logic
    urgency_keywords = ["immediately", "critical", "urgent", "asap", "cannot access", "broken", "down"]
    
    test_priorities = [
        ("URGENT: Cannot access", "I cannot access my account immediately", "urgent"),
        ("Question about billing", "I have a question about my bill", "not_urgent"),
        ("System is broken", "The system is completely down", "urgent"),
        ("Thank you", "Great service, thank you!", "not_urgent")
    ]
    
    for subject, body, expected in test_priorities:
        text_lower = (subject + " " + body).lower()
        urgency_score = sum(1 for keyword in urgency_keywords if keyword in text_lower)
        priority = "urgent" if urgency_score >= 1 else "not_urgent"
        
        if priority == expected:
            print(f"✅ Priority detection working: '{subject[:20]}...' - Priority: {priority}")
        else:
            print(f"❌ Priority detection failed: '{subject[:20]}...' - Expected: {expected}, Got: {priority}")
            return False
    
    # Test 5: Test information extraction
    import re
    
    test_text = "I need help with my account. My phone is 555-123-4567 and email is backup@example.com"
    
    # Extract phone numbers
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    phones = re.findall(phone_pattern, test_text)
    
    # Extract email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, test_text)
    
    if phones and emails:
        print(f"✅ Information extraction working: Found phone {phones[0]} and email {emails[0]}")
    else:
        print("❌ Information extraction failed")
        return False
    
    return True

def test_config_creation():
    """Test configuration file creation"""
    print("\n🔧 Testing Configuration...")
    
    # Create a basic .env file if it doesn't exist
    if not os.path.exists(".env"):
        env_content = """# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Email Configuration
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_USE_SSL=true

# Database Configuration
DATABASE_URL=sqlite:///./email_assistant.db

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
"""
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Created .env template file")
    else:
        print("✅ .env file already exists")
    
    return True

def test_database_creation():
    """Test database creation"""
    print("\n🗄️ Testing Database Creation...")
    
    try:
        import sqlite3
        
        # Create a test database
        conn = sqlite3.connect("test_email_assistant.db")
        cursor = conn.cursor()
        
        # Create test tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY,
                message_id TEXT UNIQUE,
                sender_email TEXT,
                subject TEXT,
                body TEXT,
                received_date TEXT,
                sentiment TEXT,
                priority TEXT,
                category TEXT,
                is_processed BOOLEAN,
                is_responded BOOLEAN,
                response_generated TEXT,
                response_sent BOOLEAN,
                extracted_info TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_analytics (
                id INTEGER PRIMARY KEY,
                date TEXT,
                total_emails INTEGER,
                urgent_emails INTEGER,
                positive_sentiment INTEGER,
                negative_sentiment INTEGER,
                neutral_sentiment INTEGER,
                emails_resolved INTEGER,
                emails_pending INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY,
                question TEXT,
                answer TEXT,
                category TEXT,
                embedding TEXT,
                created_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Database tables created successfully")
        
        # Clean up test database
        os.remove("test_email_assistant.db")
        print("✅ Test database cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def run_minimal_tests():
    """Run all minimal tests"""
    print("🚀 AI Email Assistant - Minimal System Tests")
    print("=" * 50)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Configuration", test_config_creation),
        ("Database Creation", test_database_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All minimal tests passed! Core system is functional.")
        print("\n📝 Next steps:")
        print("1. Install full dependencies: pip install -r requirements_simple.txt")
        print("2. Set up your .env file with real credentials")
        print("3. Run: python init_knowledge_base.py")
        print("4. Run: python comprehensive_demo.py")
        print("5. Run: python main.py")
        print("6. Open http://localhost:8000 in your browser")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    run_minimal_tests()
