"""
Gmail API Service for Real-time Email Integration
Provides live email sync with Gmail accounts
"""

import os
import base64
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    print("⚠️  Gmail API libraries not installed. Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

from models import EmailBase
from ai_service import AIService

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

class GmailService:
    def __init__(self):
        self.service = None
        self.ai_service = AIService()
        self.logger = logging.getLogger(__name__)
        
    def authenticate(self, credentials_file: str = "credentials.json", token_file: str = "token.json") -> bool:
        """Authenticate with Gmail API"""
        if not GMAIL_AVAILABLE:
            self.logger.error("Gmail API libraries not available")
            return False
            
        creds = None
        
        # Load existing token
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
            
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_file):
                    self.logger.error(f"Credentials file {credentials_file} not found")
                    return False
                    
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
                
            # Save credentials for next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
                
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info("✅ Gmail API authenticated successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to build Gmail service: {e}")
            return False
    
    def get_support_emails(self, max_results: int = 50) -> List[EmailBase]:
        """Fetch support emails from Gmail"""
        if not self.service:
            self.logger.error("Gmail service not authenticated")
            return []
            
        try:
            # Search for support-related emails
            query = "subject:(support OR help OR query OR request OR issue OR problem) OR body:(support OR help OR query OR request OR issue OR problem)"
            
            # Get messages
            results = self.service.users().messages().list(
                userId='me', 
                q=query, 
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                try:
                    email_data = self._parse_message(message['id'])
                    if email_data:
                        emails.append(email_data)
                except Exception as e:
                    self.logger.error(f"Error parsing message {message['id']}: {e}")
                    continue
                    
            self.logger.info(f"✅ Fetched {len(emails)} support emails from Gmail")
            return emails
            
        except HttpError as error:
            self.logger.error(f"Gmail API error: {error}")
            return []
    
    def _parse_message(self, message_id: str) -> Optional[EmailBase]:
        """Parse Gmail message into EmailData"""
        try:
            message = self.service.users().messages().get(
                userId='me', 
                id=message_id, 
                format='full'
            ).execute()
            
            headers = message['payload'].get('headers', [])
            
            # Extract headers
            subject = ""
            sender = ""
            date = ""
            
            for header in headers:
                name = header['name'].lower()
                if name == 'subject':
                    subject = header['value']
                elif name == 'from':
                    sender = header['value']
                elif name == 'date':
                    date = header['value']
            
            # Extract body
            body = self._extract_body(message['payload'])
            
            # Parse date
            try:
                from email.utils import parsedate_to_datetime
                parsed_date = parsedate_to_datetime(date)
            except:
                parsed_date = datetime.now()
            
            # Create EmailBase
            email_data = EmailBase(
                sender_email=sender,
                subject=subject,
                body=body,
                received_date=parsed_date
            )
            
            # Process with AI
            email_data = self.ai_service.process_email(email_data)
            
            return email_data
            
        except Exception as e:
            self.logger.error(f"Error parsing message {message_id}: {e}")
            return None
    
    def _extract_body(self, payload: dict) -> str:
        """Extract email body from Gmail payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
                elif part['mimeType'] == 'text/html' and not body:
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            if payload['mimeType'] == 'text/plain':
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body
    
    def send_reply(self, to_email: str, subject: str, body: str, thread_id: str = None) -> bool:
        """Send email reply via Gmail API"""
        if not self.service:
            self.logger.error("Gmail service not authenticated")
            return False
            
        try:
            # Create message
            message = self._create_message(to_email, subject, body, thread_id)
            
            # Send message
            sent_message = self.service.users().messages().send(
                userId='me', 
                body=message
            ).execute()
            
            self.logger.info(f"✅ Reply sent successfully: {sent_message['id']}")
            return True
            
        except HttpError as error:
            self.logger.error(f"Failed to send reply: {error}")
            return False
    
    def _create_message(self, to_email: str, subject: str, body: str, thread_id: str = None) -> dict:
        """Create Gmail message"""
        message = f"To: {to_email}\r\n"
        message += f"Subject: {subject}\r\n"
        message += "Content-Type: text/html; charset=utf-8\r\n"
        message += "\r\n"
        message += body
        
        raw_message = base64.urlsafe_b64encode(message.encode('utf-8')).decode('utf-8')
        
        gmail_message = {
            'raw': raw_message
        }
        
        if thread_id:
            gmail_message['threadId'] = thread_id
            
        return gmail_message

# Demo function for testing
def demo_gmail_integration():
    """Demo Gmail integration with sample data"""
    print("🚀 Gmail API Integration Demo")
    print("=" * 50)
    
    gmail_service = GmailService()
    
    # Check if credentials are available
    if not os.path.exists("credentials.json"):
        print("⚠️  Gmail credentials.json not found")
        print("📝 To enable real Gmail integration:")
        print("   1. Go to Google Cloud Console")
        print("   2. Enable Gmail API")
        print("   3. Create OAuth 2.0 credentials")
        print("   4. Download credentials.json")
        print("   5. Run this script again")
        return
    
    # Authenticate
    if gmail_service.authenticate():
        print("✅ Gmail authentication successful")
        
        # Fetch emails
        emails = gmail_service.get_support_emails(max_results=5)
        
        if emails:
            print(f"📧 Found {len(emails)} support emails:")
            for i, email in enumerate(emails, 1):
                print(f"\n{i}. From: {email.sender}")
                print(f"   Subject: {email.subject}")
                print(f"   Priority: {email.priority}")
                print(f"   Sentiment: {email.sentiment}")
                print(f"   AI Response: {email.ai_response[:100]}...")
        else:
            print("📭 No support emails found")
    else:
        print("❌ Gmail authentication failed")

if __name__ == "__main__":
    demo_gmail_integration()
