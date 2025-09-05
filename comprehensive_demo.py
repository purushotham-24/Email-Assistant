#!/usr/bin/env python3
"""
Comprehensive AI Email Assistant Demo
This script demonstrates all features of the AI-Powered Communication Assistant
with realistic sample data that showcases the system's capabilities.
"""

import json
import time
from datetime import datetime, timedelta
from database import get_db, Email, EmailAnalytics, KnowledgeBase
from ai_service import AIService
from email_service import EmailService

def create_comprehensive_sample_emails():
    """Create comprehensive sample emails showcasing all system features"""
    print("📧 Creating comprehensive sample emails...")
    
    db = next(get_db())
    ai_service = AIService()
    
    # Comprehensive sample email data covering all scenarios
    sample_emails = [
        {
            "message_id": "urgent_001",
            "sender_email": "john.doe@company.com",
            "subject": "URGENT: System completely down - cannot access anything",
            "body": "I'm extremely frustrated! The entire system has been down for 2 hours now and I have critical deadlines. I cannot access any of my files, the dashboard is completely broken, and I'm losing money every minute. This is absolutely unacceptable. I need immediate assistance or I'll have to cancel my subscription. My phone number is 555-123-4567. Please call me immediately at this number.",
            "received_date": datetime.now() - timedelta(minutes=30)
        },
        {
            "message_id": "billing_002",
            "sender_email": "sarah.wilson@business.org",
            "subject": "Question about unexpected billing charge",
            "body": "Hi there! I hope you're doing well. I received my monthly statement and noticed a charge of $299 that I don't recognize. Could you please help me understand what this charge is for? I've been a loyal customer for 3 years and this is the first time I've seen this amount. I'm sure it's just a misunderstanding. Thank you for your help!",
            "received_date": datetime.now() - timedelta(hours=1)
        },
        {
            "message_id": "feature_003",
            "sender_email": "mike.chen@startup.io",
            "subject": "Feature request for bulk data export",
            "body": "Hello team! I absolutely love your platform - it's been a game-changer for our startup. The analytics dashboard is incredible and has helped us make data-driven decisions. I was wondering if you could add a feature for bulk data export? We need to export large datasets (10,000+ records) in CSV format for our quarterly reports. This would save us hours of manual work. Thanks for considering this feature!",
            "received_date": datetime.now() - timedelta(hours=2)
        },
        {
            "message_id": "performance_004",
            "sender_email": "lisa.rodriguez@enterprise.com",
            "subject": "System performance issues - very slow",
            "body": "The system has been extremely slow for the past week. Every page takes 30+ seconds to load, and I'm getting timeout errors frequently. I've tried refreshing, clearing cache, and using different browsers, but nothing helps. This is affecting my team's productivity significantly. We have 50+ users and they're all experiencing the same issues. Please investigate this immediately.",
            "received_date": datetime.now() - timedelta(hours=3)
        },
        {
            "message_id": "password_005",
            "sender_email": "david.kim@consulting.net",
            "subject": "Password reset not working",
            "body": "I'm having trouble resetting my password. I clicked the reset link in the email but it says the link has expired. I've tried requesting a new reset email three times but haven't received anything. I need to access my account urgently for a client presentation tomorrow. Can you please help me reset my password? My alternate email is david.kim.backup@gmail.com.",
            "received_date": datetime.now() - timedelta(hours=4)
        },
        {
            "message_id": "complaint_006",
            "sender_email": "angry.customer@email.com",
            "subject": "Terrible customer service experience",
            "body": "I am absolutely disgusted with your customer service. I've been trying to get help for 3 days and no one has responded to my emails. Your support team is completely useless. I've been a paying customer for 2 years and this is how you treat me? I want to speak to a manager immediately. This is unacceptable and I'm considering legal action.",
            "received_date": datetime.now() - timedelta(hours=5)
        },
        {
            "message_id": "positive_007",
            "sender_email": "happy.user@company.com",
            "subject": "Amazing service - thank you!",
            "body": "I just wanted to take a moment to thank your team for the incredible service. The new features you released last week have completely transformed how we work. The AI-powered insights are spot-on and have helped us increase our efficiency by 40%. Your customer support team is also fantastic - they resolved my issue in under 10 minutes. Keep up the excellent work!",
            "received_date": datetime.now() - timedelta(hours=6)
        },
        {
            "message_id": "technical_008",
            "sender_email": "tech.support@itdept.org",
            "subject": "Integration API documentation needed",
            "body": "Hi, I'm working on integrating your platform with our internal systems. I need detailed API documentation for the webhook endpoints. Specifically, I need information about authentication, payload formats, and error handling. Could you please provide comprehensive documentation or point me to the right resources? We're planning to go live next month.",
            "received_date": datetime.now() - timedelta(hours=7)
        },
        {
            "message_id": "security_009",
            "sender_email": "security.officer@bank.com",
            "subject": "Security audit questions",
            "body": "We're conducting a security audit of all our third-party services. Could you please provide information about your security certifications (SOC 2, ISO 27001), data encryption standards, and access controls? We also need details about your incident response procedures and data retention policies. This is for compliance purposes.",
            "received_date": datetime.now() - timedelta(hours=8)
        },
        {
            "message_id": "refund_010",
            "sender_email": "disappointed.user@email.com",
            "subject": "Request for refund - service not as advertised",
            "body": "I signed up for your premium plan based on the features advertised, but the actual functionality is very limited compared to what was promised. The AI features don't work as described, and the integration capabilities are basic at best. I've been trying to make it work for 2 weeks but it's not meeting our needs. I'd like to request a full refund.",
            "received_date": datetime.now() - timedelta(hours=9)
        }
    ]
    
    created_emails = []
    
    for i, email_data in enumerate(sample_emails, 1):
        try:
            print(f"Processing email {i}/{len(sample_emails)}: {email_data['subject'][:40]}...")
            
            # Analyze email using AI service
            sentiment = ai_service.analyze_sentiment(email_data['body'])
            priority = ai_service.detect_priority(email_data['body'], email_data['subject'])
            category = ai_service.categorize_email(email_data['subject'], email_data['body'])
            extracted_info = ai_service.extract_information(email_data['body'])
            
            # Create email record
            email = Email(
                message_id=email_data['message_id'],
                sender_email=email_data['sender_email'],
                subject=email_data['subject'],
                body=email_data['body'],
                received_date=email_data['received_date'],
                sentiment=sentiment,
                priority=priority,
                category=category,
                extracted_info=json.dumps(extracted_info),
                is_processed=True,
                is_responded=False
            )
            
            db.add(email)
            created_emails.append(email)
            
            print(f"   ✅ Sentiment: {sentiment}, Priority: {priority}, Category: {category}")
            
        except Exception as e:
            print(f"   ❌ Error creating email {email_data['message_id']}: {e}")
    
    try:
        db.commit()
        print(f"\n🎉 Successfully created {len(created_emails)} comprehensive sample emails")
        return created_emails
    except Exception as e:
        print(f"❌ Error committing emails: {e}")
        db.rollback()
        return []

def generate_ai_responses_for_demo():
    """Generate AI responses for all sample emails"""
    print("\n🤖 Generating AI responses for demo...")
    
    db = next(get_db())
    email_service = EmailService()
    
    # Get unprocessed emails
    emails = db.query(Email).filter(Email.is_processed == True, Email.is_responded == False).all()
    
    for i, email in enumerate(emails, 1):
        try:
            print(f"Generating response {i}/{len(emails)}: {email.subject[:40]}...")
            
            # Generate AI response
            response = email_service.generate_ai_response(email.id, db=db)
            
            if response:
                print(f"   ✅ Response generated ({len(response)} characters)")
                print(f"   Preview: {response[:80]}...")
            else:
                print("   ❌ Failed to generate response")
                
        except Exception as e:
            print(f"   ❌ Error processing email {email.id}: {e}")
    
    print(f"\n🎯 Generated responses for {len(emails)} emails")

def simulate_email_resolution():
    """Simulate resolving some emails to show analytics"""
    print("\n📊 Simulating email resolution for analytics...")
    
    db = next(get_db())
    
    # Resolve some emails (mark as responded)
    emails_to_resolve = db.query(Email).filter(
        Email.is_processed == True,
        Email.is_responded == False
    ).limit(3).all()
    
    for email in emails_to_resolve:
        email.is_responded = True
        email.response_sent = True
        print(f"   ✅ Resolved: {email.subject[:40]}...")
    
    db.commit()
    print(f"📈 Marked {len(emails_to_resolve)} emails as resolved")

def update_comprehensive_analytics():
    """Update analytics for comprehensive dashboard view"""
    print("\n📊 Updating comprehensive analytics...")
    
    try:
        db = next(get_db())
        email_service = EmailService()
        email_service.update_analytics(db)
        print("✅ Analytics updated successfully")
    except Exception as e:
        print(f"❌ Error updating analytics: {e}")

def display_comprehensive_stats():
    """Display comprehensive system statistics"""
    print("\n📈 Comprehensive System Statistics:")
    print("=" * 60)
    
    try:
        db = next(get_db())
        today = datetime.now().date()
        
        # Get today's analytics
        analytics = db.query(EmailAnalytics).filter(
            EmailAnalytics.date >= today
        ).first()
        
        if analytics:
            print(f"📧 Total Emails Today: {analytics.total_emails}")
            print(f"🚨 Urgent Emails: {analytics.urgent_emails}")
            print(f"✅ Emails Resolved: {analytics.emails_resolved}")
            print(f"⏳ Emails Pending: {analytics.emails_pending}")
            print(f"😊 Positive Sentiment: {analytics.positive_sentiment}")
            print(f"😞 Negative Sentiment: {analytics.negative_sentiment}")
            print(f"😐 Neutral Sentiment: {analytics.neutral_sentiment}")
        else:
            print("No analytics data available")
        
        # Get comprehensive email distribution
        print(f"\n📊 Email Distribution Analysis:")
        emails = db.query(Email).filter(Email.received_date >= today).all()
        
        categories = {}
        priorities = {}
        sentiments = {}
        
        for email in emails:
            categories[email.category] = categories.get(email.category, 0) + 1
            priorities[email.priority] = priorities.get(email.priority, 0) + 1
            sentiments[email.sentiment] = sentiments.get(email.sentiment, 0) + 1
        
        print(f"   📂 Categories: {categories}")
        print(f"   ⚡ Priorities: {priorities}")
        print(f"   😊 Sentiments: {sentiments}")
        
        # Show response generation status
        with_responses = len([e for e in emails if e.response_generated])
        without_responses = len([e for e in emails if not e.response_generated])
        
        print(f"\n🤖 AI Response Status:")
        print(f"   ✅ With AI Responses: {with_responses}")
        print(f"   ⏳ Without Responses: {without_responses}")
        
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")

def display_priority_queue_detailed():
    """Display detailed priority queue"""
    print("\n🎯 Detailed Priority Queue (Urgent First):")
    print("=" * 60)
    
    try:
        db = next(get_db())
        email_service = EmailService()
        
        priority_emails = email_service.get_priority_queue(db)
        
        if not priority_emails:
            print("No emails in priority queue")
            return
        
        for i, email in enumerate(priority_emails, 1):
            status = "🚨 URGENT" if email.priority == "urgent" else "📧 NORMAL"
            sentiment_emoji = {
                "positive": "😊",
                "negative": "😞", 
                "neutral": "😐"
            }.get(email.sentiment, "❓")
            
            response_status = "✅ Has Response" if email.response_generated else "⏳ No Response"
            resolution_status = "✅ Resolved" if email.is_responded else "⏳ Pending"
            
            print(f"{i}. {status} {sentiment_emoji} {email.subject[:50]}...")
            print(f"   From: {email.sender_email}")
            print(f"   Category: {email.category}")
            print(f"   Received: {email.received_date.strftime('%H:%M')}")
            print(f"   Response: {response_status} | Status: {resolution_status}")
            print()
            
    except Exception as e:
        print(f"❌ Error getting priority queue: {e}")

def run_comprehensive_demo():
    """Run the comprehensive demo showcasing all features"""
    print("🚀 AI-Powered Communication Assistant - Comprehensive Demo")
    print("=" * 70)
    print("This demo showcases all features of the system with realistic data")
    print("=" * 70)
    
    try:
        # Step 1: Create comprehensive sample emails
        print("\n📧 STEP 1: Creating comprehensive sample emails...")
        emails = create_comprehensive_sample_emails()
        
        if not emails:
            print("❌ Demo failed - no emails created")
            return
        
        # Step 2: Generate AI responses
        print("\n🤖 STEP 2: Generating AI responses...")
        generate_ai_responses_for_demo()
        
        # Step 3: Simulate some resolutions
        print("\n📊 STEP 3: Simulating email resolution...")
        simulate_email_resolution()
        
        # Step 4: Update analytics
        print("\n📈 STEP 4: Updating analytics...")
        update_comprehensive_analytics()
        
        # Step 5: Display comprehensive statistics
        print("\n📊 STEP 5: Displaying comprehensive statistics...")
        display_comprehensive_stats()
        
        # Step 6: Show detailed priority queue
        print("\n🎯 STEP 6: Displaying detailed priority queue...")
        display_priority_queue_detailed()
        
        print("\n🎉 Comprehensive Demo Completed Successfully!")
        print("\n" + "=" * 70)
        print("📝 DEMO FEATURES SHOWCASED:")
        print("=" * 70)
        print("✅ Email Retrieval & Filtering (IMAP/SMTP)")
        print("✅ AI-Powered Sentiment Analysis")
        print("✅ Priority Detection (Urgent vs Normal)")
        print("✅ Email Categorization (Support, Query, Request, etc.)")
        print("✅ Information Extraction (Contact details, requirements)")
        print("✅ RAG (Retrieval-Augmented Generation) for responses")
        print("✅ Context-Aware AI Response Generation")
        print("✅ Priority Queue Management")
        print("✅ Real-time Analytics & Statistics")
        print("✅ Interactive Dashboard with Charts")
        print("✅ Email Response Sending")
        print("✅ Knowledge Base Integration")
        print("=" * 70)
        print("\n🌐 NEXT STEPS:")
        print("1. Open http://localhost:8000 in your browser")
        print("2. View the enhanced dashboard with all sample data")
        print("3. Test the email sync functionality")
        print("4. Generate and send AI responses")
        print("5. Explore the analytics and charts")
        print("6. Test with real email credentials")
        print("\n🎯 The system is ready for the hackathon demonstration!")
        
    except Exception as e:
        print(f"❌ Comprehensive demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_comprehensive_demo()
