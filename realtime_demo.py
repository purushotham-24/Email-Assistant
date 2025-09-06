"""
Real-time Email Assistant Demo
Demonstrates live Gmail integration with AI processing
"""

import os
import time
import json
from datetime import datetime
from typing import List

from gmail_service import GmailService
from ai_service import AIService
from database import DatabaseManager
from models import EmailData

class RealtimeEmailDemo:
    def __init__(self):
        self.gmail_service = GmailService()
        self.ai_service = AIService()
        self.db = DatabaseManager()
        self.running = False
        
    def start_realtime_sync(self, interval_minutes: int = 5):
        """Start real-time email synchronization"""
        print("🚀 Starting Real-time Email Assistant")
        print("=" * 50)
        
        # Check Gmail credentials
        if not os.path.exists("credentials.json"):
            print("⚠️  Gmail credentials not found. Using demo mode...")
            self._demo_mode()
            return
            
        # Authenticate with Gmail
        if not self.gmail_service.authenticate():
            print("❌ Gmail authentication failed. Using demo mode...")
            self._demo_mode()
            return
            
        print("✅ Gmail authentication successful")
        print(f"🔄 Syncing emails every {interval_minutes} minutes")
        print("📱 Press Ctrl+C to stop")
        print("-" * 50)
        
        self.running = True
        
        try:
            while self.running:
                self._sync_emails()
                self._display_stats()
                
                print(f"⏰ Next sync in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping real-time sync...")
            self.running = False
    
    def _sync_emails(self):
        """Sync emails from Gmail"""
        print(f"\n🔄 Syncing emails at {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Fetch new emails
            emails = self.gmail_service.get_support_emails(max_results=10)
            
            if emails:
                print(f"📧 Found {len(emails)} new support emails")
                
                # Process and store emails
                for email in emails:
                    self.db.store_email(email)
                    print(f"   ✅ Processed: {email.subject[:50]}...")
            else:
                print("📭 No new support emails found")
                
        except Exception as e:
            print(f"❌ Sync error: {e}")
    
    def _display_stats(self):
        """Display current statistics"""
        try:
            stats = self.db.get_analytics()
            
            print("\n📊 Current Statistics:")
            print(f"   📧 Total Emails: {stats.get('total_emails', 0)}")
            print(f"   🔥 Urgent: {stats.get('urgent_count', 0)}")
            print(f"   😊 Positive: {stats.get('positive_count', 0)}")
            print(f"   😞 Negative: {stats.get('negative_count', 0)}")
            print(f"   ✅ Resolved: {stats.get('resolved_count', 0)}")
            print(f"   ⏳ Pending: {stats.get('pending_count', 0)}")
            
        except Exception as e:
            print(f"❌ Stats error: {e}")
    
    def _demo_mode(self):
        """Run in demo mode with sample data"""
        print("🎭 Running in Demo Mode")
        print("=" * 30)
        
        # Create sample emails
        sample_emails = [
            EmailData(
                sender="customer1@example.com",
                subject="URGENT: System down - need immediate help",
                body="Our system is completely down and we need immediate assistance. This is affecting our business operations.",
                received_at=datetime.now()
            ),
            EmailData(
                sender="customer2@example.com", 
                subject="Support Request: Login issues",
                body="I'm having trouble logging into my account. Can you help me resolve this?",
                received_at=datetime.now()
            ),
            EmailData(
                sender="customer3@example.com",
                subject="Thank you for the great service!",
                body="Just wanted to say thank you for the excellent support. Everything is working perfectly now.",
                received_at=datetime.now()
            )
        ]
        
        print("📧 Processing sample emails...")
        
        for email in sample_emails:
            # Process with AI
            processed_email = self.ai_service.process_email(email)
            
            # Store in database
            self.db.store_email(processed_email)
            
            print(f"   ✅ Processed: {processed_email.subject}")
            print(f"      Priority: {processed_email.priority}")
            print(f"      Sentiment: {processed_email.sentiment}")
            print(f"      AI Response: {processed_email.ai_response[:80]}...")
            print()
        
        # Display final stats
        self._display_stats()
        
        print("\n🎯 Demo completed! To enable real Gmail integration:")
        print("   1. Set up Google Cloud Console")
        print("   2. Enable Gmail API")
        print("   3. Download credentials.json")
        print("   4. Run: python realtime_demo.py --live")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Real-time Email Assistant Demo")
    parser.add_argument("--live", action="store_true", help="Enable live Gmail integration")
    parser.add_argument("--interval", type=int, default=5, help="Sync interval in minutes")
    
    args = parser.parse_args()
    
    demo = RealtimeEmailDemo()
    
    if args.live:
        demo.start_realtime_sync(args.interval)
    else:
        demo._demo_mode()

if __name__ == "__main__":
    main()
