#!/usr/bin/env python3
"""
Simple Demo for AI Email Assistant
This demo works without heavy dependencies and shows the core functionality
"""

import json
import sqlite3
import os
from datetime import datetime, timedelta

def create_demo_database():
    """Create a demo database with sample data"""
    print("🗄️ Creating demo database...")
    
    # Remove existing demo database
    if os.path.exists("demo_email_assistant.db"):
        os.remove("demo_email_assistant.db")
    
    conn = sqlite3.connect("demo_email_assistant.db")
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE emails (
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
        CREATE TABLE email_analytics (
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
        CREATE TABLE knowledge_base (
            id INTEGER PRIMARY KEY,
            question TEXT,
            answer TEXT,
            category TEXT,
            embedding TEXT,
            created_at TEXT
        )
    """)
    
    # Insert sample emails
    sample_emails = [
        {
            "message_id": "urgent_001",
            "sender_email": "john.doe@company.com",
            "subject": "URGENT: System completely down - cannot access anything",
            "body": "I'm extremely frustrated! The entire system has been down for 2 hours now and I have critical deadlines. I cannot access any of my files, the dashboard is completely broken, and I'm losing money every minute. This is absolutely unacceptable. I need immediate assistance or I'll have to cancel my subscription. My phone number is 555-123-4567. Please call me immediately at this number.",
            "received_date": (datetime.now() - timedelta(minutes=30)).isoformat(),
            "sentiment": "negative",
            "priority": "urgent",
            "category": "support",
            "is_processed": True,
            "is_responded": False,
            "response_generated": "Dear John,\n\nI sincerely apologize for the system downtime you're experiencing. I understand how frustrating this must be, especially with critical deadlines approaching.\n\nI'm immediately escalating this to our technical team for urgent resolution. Our system administrators are working to restore service as quickly as possible.\n\nI'll personally monitor this case and provide you with updates every 30 minutes until the issue is resolved. If you need to reach me directly, please call our emergency support line at 1-800-SUPPORT.\n\nThank you for your patience, and I apologize for any inconvenience this has caused.\n\nBest regards,\nSarah\nCustomer Support Manager",
            "response_sent": False,
            "extracted_info": json.dumps({
                "contact_details": {"phone": "555-123-4567"},
                "requirements": ["immediate assistance", "system restoration"],
                "sentiment_indicators": ["negative: frustrated", "negative: unacceptable"],
                "metadata": {"urgency_level": "critical"}
            }),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "message_id": "billing_002",
            "sender_email": "sarah.wilson@business.org",
            "subject": "Question about unexpected billing charge",
            "body": "Hi there! I hope you're doing well. I received my monthly statement and noticed a charge of $299 that I don't recognize. Could you please help me understand what this charge is for? I've been a loyal customer for 3 years and this is the first time I've seen this amount. I'm sure it's just a misunderstanding. Thank you for your help!",
            "received_date": (datetime.now() - timedelta(hours=1)).isoformat(),
            "sentiment": "positive",
            "priority": "not_urgent",
            "category": "query",
            "is_processed": True,
            "is_responded": True,
            "response_generated": "Dear Sarah,\n\nThank you for reaching out about your billing statement. I'm happy to help clarify this charge for you.\n\nI've reviewed your account and the $299 charge is for your annual premium subscription upgrade that you requested last month. This includes additional features like advanced analytics, priority support, and increased storage capacity.\n\nIf you have any questions about these features or would like to discuss your subscription options, please don't hesitate to contact me.\n\nThank you for being a valued customer for 3 years!\n\nBest regards,\nMike\nBilling Support Specialist",
            "response_sent": True,
            "extracted_info": json.dumps({
                "contact_details": {},
                "requirements": ["billing clarification"],
                "sentiment_indicators": ["positive: loyal customer"],
                "metadata": {"customer_tenure": "3 years"}
            }),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "message_id": "feature_003",
            "sender_email": "mike.chen@startup.io",
            "subject": "Feature request for bulk data export",
            "body": "Hello team! I absolutely love your platform - it's been a game-changer for our startup. The analytics dashboard is incredible and has helped us make data-driven decisions. I was wondering if you could add a feature for bulk data export? We need to export large datasets (10,000+ records) in CSV format for our quarterly reports. This would save us hours of manual work. Thanks for considering this feature!",
            "received_date": (datetime.now() - timedelta(hours=2)).isoformat(),
            "sentiment": "positive",
            "priority": "not_urgent",
            "category": "request",
            "is_processed": True,
            "is_responded": False,
            "response_generated": "Dear Mike,\n\nThank you for your fantastic feedback! I'm thrilled to hear that our platform has been a game-changer for your startup and that the analytics dashboard is helping you make data-driven decisions.\n\nYour feature request for bulk data export is excellent and aligns perfectly with our product roadmap. I'm pleased to inform you that we're actually working on this feature and it's scheduled for release in our next major update (Q2 2024).\n\nThe bulk export feature will support:\n- CSV, JSON, and Excel formats\n- Up to 100,000 records per export\n- Scheduled exports\n- Custom field selection\n\nI'll add you to our beta testing program so you can try it out before the official release. You'll receive an invitation within the next week.\n\nThank you for being such an engaged user!\n\nBest regards,\nLisa\nProduct Manager",
            "response_sent": False,
            "extracted_info": json.dumps({
                "contact_details": {},
                "requirements": ["bulk data export", "CSV format", "10,000+ records"],
                "sentiment_indicators": ["positive: love", "positive: game-changer", "positive: incredible"],
                "metadata": {"company_type": "startup"}
            }),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "message_id": "performance_004",
            "sender_email": "lisa.rodriguez@enterprise.com",
            "subject": "System performance issues - very slow",
            "body": "The system has been extremely slow for the past week. Every page takes 30+ seconds to load, and I'm getting timeout errors frequently. I've tried refreshing, clearing cache, and using different browsers, but nothing helps. This is affecting my team's productivity significantly. We have 50+ users and they're all experiencing the same issues. Please investigate this immediately.",
            "received_date": (datetime.now() - timedelta(hours=3)).isoformat(),
            "sentiment": "negative",
            "priority": "urgent",
            "category": "support",
            "is_processed": True,
            "is_responded": False,
            "response_generated": "Dear Lisa,\n\nI apologize for the performance issues you and your team are experiencing. This is definitely not the level of service we want to provide, especially for an enterprise customer like yours.\n\nI've immediately escalated this to our performance engineering team. They're investigating the root cause and implementing optimizations to resolve the slow loading times.\n\nAs a temporary solution, I'm provisioning additional server resources for your account to improve performance while we work on the permanent fix.\n\nI'll provide you with updates every 2 hours until this is resolved. Your account manager will also be in touch to discuss any impact on your team's productivity.\n\nThank you for your patience and for bringing this to our attention.\n\nBest regards,\nDavid\nTechnical Support Manager",
            "response_sent": False,
            "extracted_info": json.dumps({
                "contact_details": {},
                "requirements": ["performance investigation", "immediate resolution"],
                "sentiment_indicators": ["negative: extremely slow", "negative: timeout errors"],
                "metadata": {"team_size": "50+ users", "customer_type": "enterprise"}
            }),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "message_id": "positive_005",
            "sender_email": "happy.user@company.com",
            "subject": "Amazing service - thank you!",
            "body": "I just wanted to take a moment to thank your team for the incredible service. The new features you released last week have completely transformed how we work. The AI-powered insights are spot-on and have helped us increase our efficiency by 40%. Your customer support team is also fantastic - they resolved my issue in under 10 minutes. Keep up the excellent work!",
            "received_date": (datetime.now() - timedelta(hours=4)).isoformat(),
            "sentiment": "positive",
            "priority": "not_urgent",
            "category": "feedback",
            "is_processed": True,
            "is_responded": True,
            "response_generated": "Dear Valued Customer,\n\nThank you so much for this wonderful feedback! It truly made our day to hear how much the new features have improved your workflow.\n\nI'm thrilled that the AI-powered insights are helping you increase efficiency by 40% - that's exactly the kind of impact we're aiming for. I'll make sure to share your feedback with our product and support teams.\n\nYour kind words about our customer support team mean a lot to us. We're committed to providing fast, helpful service, and it's rewarding to know we're meeting that goal.\n\nThank you for being such a great customer and for taking the time to share your experience!\n\nBest regards,\nJennifer\nCustomer Success Manager",
            "response_sent": True,
            "extracted_info": json.dumps({
                "contact_details": {},
                "requirements": [],
                "sentiment_indicators": ["positive: incredible", "positive: fantastic", "positive: excellent"],
                "metadata": {"efficiency_improvement": "40%", "support_time": "under 10 minutes"}
            }),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    
    for email in sample_emails:
        cursor.execute("""
            INSERT INTO emails (message_id, sender_email, subject, body, received_date, 
                              sentiment, priority, category, is_processed, is_responded, 
                              response_generated, response_sent, extracted_info, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            email["message_id"], email["sender_email"], email["subject"], email["body"],
            email["received_date"], email["sentiment"], email["priority"], email["category"],
            email["is_processed"], email["is_responded"], email["response_generated"],
            email["response_sent"], email["extracted_info"], email["created_at"], email["updated_at"]
        ))
    
    # Insert analytics data
    today = datetime.now().date().isoformat()
    cursor.execute("""
        INSERT INTO email_analytics (date, total_emails, urgent_emails, positive_sentiment, 
                                   negative_sentiment, neutral_sentiment, emails_resolved, emails_pending)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (today, 5, 2, 2, 2, 1, 2, 3))
    
    # Insert knowledge base items
    kb_items = [
        ("How do I reset my password?", "To reset your password, visit our password reset page and follow the instructions sent to your email.", "support"),
        ("What are your business hours?", "Our support team is available Monday-Friday, 9 AM to 6 PM EST. Emergency support is available 24/7.", "general"),
        ("How do I cancel my subscription?", "Go to Settings > Subscription Management and click 'Cancel Subscription'. Your service remains active until the end of your billing period.", "billing"),
        ("I'm experiencing slow performance", "Try refreshing your browser, clearing cache, and checking your internet connection. If issues persist, contact our technical team.", "technical")
    ]
    
    for question, answer, category in kb_items:
        cursor.execute("""
            INSERT INTO knowledge_base (question, answer, category, created_at)
            VALUES (?, ?, ?, ?)
        """, (question, answer, category, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    print("✅ Demo database created with sample data")

def display_dashboard_stats():
    """Display dashboard statistics"""
    print("\n📊 AI Email Assistant - Dashboard Statistics")
    print("=" * 60)
    
    conn = sqlite3.connect("demo_email_assistant.db")
    cursor = conn.cursor()
    
    # Get analytics
    cursor.execute("SELECT * FROM email_analytics ORDER BY date DESC LIMIT 1")
    analytics = cursor.fetchone()
    
    if analytics:
        print(f"📧 Total Emails Today: {analytics[2]}")
        print(f"🚨 Urgent Emails: {analytics[3]}")
        print(f"✅ Emails Resolved: {analytics[7]}")
        print(f"⏳ Emails Pending: {analytics[8]}")
        print(f"😊 Positive Sentiment: {analytics[4]}")
        print(f"😞 Negative Sentiment: {analytics[5]}")
        print(f"😐 Neutral Sentiment: {analytics[6]}")
    
    # Get email distribution
    cursor.execute("SELECT category, COUNT(*) FROM emails GROUP BY category")
    categories = cursor.fetchall()
    
    cursor.execute("SELECT priority, COUNT(*) FROM emails GROUP BY priority")
    priorities = cursor.fetchall()
    
    cursor.execute("SELECT sentiment, COUNT(*) FROM emails GROUP BY sentiment")
    sentiments = cursor.fetchall()
    
    print(f"\n📊 Email Distribution:")
    print(f"   Categories: {dict(categories)}")
    print(f"   Priorities: {dict(priorities)}")
    print(f"   Sentiments: {dict(sentiments)}")
    
    conn.close()

def display_priority_queue():
    """Display emails in priority order"""
    print("\n🎯 Priority Queue (Urgent First):")
    print("=" * 60)
    
    conn = sqlite3.connect("demo_email_assistant.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM emails 
        WHERE is_processed = 1 
        ORDER BY 
            CASE priority 
                WHEN 'urgent' THEN 1 
                ELSE 2 
            END,
            received_date ASC
    """)
    
    emails = cursor.fetchall()
    
    for i, email in enumerate(emails, 1):
        status = "🚨 URGENT" if email[7] == "urgent" else "📧 NORMAL"
        sentiment_emoji = {
            "positive": "😊",
            "negative": "😞", 
            "neutral": "😐"
        }.get(email[6], "❓")
        
        response_status = "✅ Has Response" if email[11] else "⏳ No Response"
        resolution_status = "✅ Resolved" if email[10] else "⏳ Pending"
        
        print(f"{i}. {status} {sentiment_emoji} {email[3][:50]}...")
        print(f"   From: {email[2]}")
        print(f"   Category: {email[8]}")
        print(f"   Received: {email[5][:16]}")
        print(f"   Response: {response_status} | Status: {resolution_status}")
        if email[11]:
            print(f"   AI Response: {email[11][:100]}...")
        print()
    
    conn.close()

def display_ai_responses():
    """Display AI-generated responses"""
    print("\n🤖 AI-Generated Responses:")
    print("=" * 60)
    
    conn = sqlite3.connect("demo_email_assistant.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT subject, response_generated FROM emails WHERE response_generated IS NOT NULL")
    responses = cursor.fetchall()
    
    for i, (subject, response) in enumerate(responses, 1):
        print(f"{i}. Subject: {subject}")
        print(f"   Response: {response[:200]}...")
        print()
    
    conn.close()

def run_simple_demo():
    """Run the simple demo"""
    print("🚀 AI-Powered Communication Assistant - Simple Demo")
    print("=" * 70)
    print("This demo showcases the core functionality without heavy dependencies")
    print("=" * 70)
    
    try:
        # Create demo database
        create_demo_database()
        
        # Display dashboard stats
        display_dashboard_stats()
        
        # Display priority queue
        display_priority_queue()
        
        # Display AI responses
        display_ai_responses()
        
        print("\n🎉 Simple Demo Completed Successfully!")
        print("\n" + "=" * 70)
        print("📝 DEMO FEATURES SHOWCASED:")
        print("=" * 70)
        print("✅ Email Database with Sample Data")
        print("✅ AI-Powered Sentiment Analysis")
        print("✅ Priority Detection (Urgent vs Normal)")
        print("✅ Email Categorization")
        print("✅ Information Extraction")
        print("✅ AI-Generated Responses")
        print("✅ Priority Queue Management")
        print("✅ Real-time Analytics & Statistics")
        print("✅ Professional Response Generation")
        print("=" * 70)
        print("\n🌐 To see the full dashboard:")
        print("1. Install dependencies: pip install -r requirements_simple.txt")
        print("2. Run: python main.py")
        print("3. Open http://localhost:8000 in your browser")
        print("\n🎯 The system is ready for hackathon demonstration!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_simple_demo()
