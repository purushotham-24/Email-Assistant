import imaplib
import email
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from config import settings
from database import Email, EmailAnalytics, get_db
from ai_service import AIService
from sqlalchemy.orm import Session
import smtplib
from email.mime.text import MIMEText

class EmailService:
    def __init__(self):
        self.ai_service = AIService()
        self.imap_server = None
        self.smtp_server = None
        
    def connect_imap(self) -> bool:
        """Connect to IMAP server"""
        try:
            if settings.EMAIL_USE_SSL:
                self.imap_server = imaplib.IMAP4_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
            else:
                self.imap_server = imaplib.IMAP4(settings.EMAIL_HOST, settings.EMAIL_PORT)
            
            self.imap_server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            return True
        except Exception as e:
            print(f"IMAP connection failed: {e}")
            return False
    
    def connect_smtp(self) -> bool:
        """Connect to SMTP server for sending emails"""
        try:
            if settings.EMAIL_USE_SSL:
                self.smtp_server = smtplib.SMTP_SSL(settings.EMAIL_HOST, 465)
            else:
                self.smtp_server = smtplib.SMTP(settings.EMAIL_HOST, 587)
                self.smtp_server.starttls()
            
            self.smtp_server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            return True
        except Exception as e:
            print(f"SMTP connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from email servers"""
        if self.imap_server:
            try:
                self.imap_server.logout()
            except:
                pass
        if self.smtp_server:
            try:
                self.smtp_server.quit()
            except:
                pass
    
    def is_support_email(self, subject: str, body: str) -> bool:
        """Check if email is support-related based on keywords"""
        text_lower = (subject + " " + body).lower()
        return any(keyword in text_lower for keyword in settings.SUPPORT_KEYWORDS)
    
    def fetch_emails(self, hours_back: int = 24) -> List[Dict]:
        """Fetch emails from the last N hours"""
        if not self.connect_imap():
            return []
        
        try:
            self.imap_server.select('INBOX')
            
            # Calculate date range
            date_since = (datetime.now() - timedelta(hours=hours_back)).strftime("%d-%b-%Y")
            
            # Search for emails since date
            _, message_numbers = self.imap_server.search(None, f'(SINCE {date_since})')
            
            emails = []
            for num in message_numbers[0].split():
                try:
                    _, msg_data = self.imap_server.fetch(num, '(RFC822)')
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Extract email details
                    subject = email_message.get('Subject', '')
                    sender = email_message.get('From', '')
                    date_str = email_message.get('Date', '')
                    message_id = email_message.get('Message-ID', '')
                    
                    # Parse date
                    try:
                        parsed_date = email.utils.parsedate_to_datetime(date_str)
                    except:
                        parsed_date = datetime.now()
                    
                    # Get email body
                    body = ""
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = email_message.get_payload(decode=True).decode()
                    
                    # Check if it's a support email
                    if self.is_support_email(subject, body):
                        emails.append({
                            'message_id': message_id,
                            'sender_email': sender,
                            'subject': subject,
                            'body': body,
                            'received_date': parsed_date
                        })
                
                except Exception as e:
                    print(f"Error processing email {num}: {e}")
                    continue
            
            return emails
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
        finally:
            self.disconnect()
    
    def process_emails(self, emails: List[Dict], db: Session) -> int:
        """Process emails using AI service and store in database"""
        processed_count = 0
        
        for email_data in emails:
            try:
                # Check if email already exists
                existing_email = db.query(Email).filter(
                    Email.message_id == email_data['message_id']
                ).first()
                
                if existing_email:
                    continue
                
                # Analyze email using AI
                sentiment = self.ai_service.analyze_sentiment(email_data['body'])
                priority = self.ai_service.detect_priority(email_data['body'], email_data['subject'])
                category = self.ai_service.categorize_email(email_data['subject'], email_data['body'])
                extracted_info = self.ai_service.extract_information(email_data['body'])
                
                # Create email record
                new_email = Email(
                    message_id=email_data['message_id'],
                    sender_email=email_data['sender_email'],
                    subject=email_data['subject'],
                    body=email_data['body'],
                    received_date=email_data['received_date'],
                    sentiment=sentiment,
                    priority=priority,
                    category=category,
                    extracted_info=json.dumps(extracted_info),
                    is_processed=True
                )
                
                db.add(new_email)
                processed_count += 1
                
            except Exception as e:
                print(f"Error processing email {email_data.get('message_id', 'unknown')}: {e}")
                continue
        
        try:
            db.commit()
        except Exception as e:
            print(f"Error committing to database: {e}")
            db.rollback()
        
        return processed_count
    
    def generate_ai_response(self, email_id: int, custom_prompt: str = None, db: Session = None) -> Optional[str]:
        """Generate AI response for a specific email"""
        if not db:
            db = next(get_db())
        
        email_record = db.query(Email).filter(Email.id == email_id).first()
        if not email_record:
            return None
        
        try:
            response, confidence, reasoning = self.ai_service.generate_response(
                email_record.body,
                email_record.subject,
                email_record.sender_email,
                email_record.sentiment,
                email_record.priority,
                email_record.category,
                custom_prompt
            )
            
            # Update email record
            email_record.response_generated = response
            email_record.is_processed = True
            db.commit()
            
            return response
            
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return None
    
    def send_email_response(self, email_id: int, custom_response: str = None, db: Session = None) -> bool:
        """Send email response to customer"""
        if not db:
            db = next(get_db())
        
        email_record = db.query(Email).filter(Email.id == email_id).first()
        if not email_record:
            return False
        
        try:
            if not self.connect_smtp():
                return False
            
            # Prepare email
            msg = MIMEMultipart()
            msg['From'] = settings.EMAIL_USERNAME
            msg['To'] = email_record.sender_email
            msg['Subject'] = f"Re: {email_record.subject}"
            
            # Use custom response or generated response
            response_text = custom_response or email_record.response_generated
            if not response_text:
                return False
            
            msg.attach(MIMEText(response_text, 'plain'))
            
            # Send email
            self.smtp_server.send_message(msg)
            
            # Update database
            email_record.response_sent = True
            email_record.is_responded = True
            db.commit()
            
            return True
            
        except Exception as e:
            print(f"Error sending email response: {e}")
            return False
        finally:
            self.disconnect()
    
    def get_priority_queue(self, db: Session) -> List[Email]:
        """Get emails in priority order (urgent first)"""
        return db.query(Email).filter(
            Email.is_processed == True,
            Email.is_responded == False
        ).order_by(
            Email.priority.desc(),
            Email.received_date.asc()
        ).all()
    
    def update_analytics(self, db: Session):
        """Update email analytics for dashboard"""
        today = datetime.now().date()
        
        # Get today's analytics
        analytics = db.query(EmailAnalytics).filter(
            EmailAnalytics.date >= today
        ).first()
        
        if not analytics:
            analytics = EmailAnalytics(date=today)
            db.add(analytics)
        
        # Calculate statistics
        total_emails = db.query(Email).filter(
            Email.received_date >= today
        ).count()
        
        urgent_emails = db.query(Email).filter(
            Email.received_date >= today,
            Email.priority == 'urgent'
        ).count()
        
        positive_sentiment = db.query(Email).filter(
            Email.received_date >= today,
            Email.sentiment == 'positive'
        ).count()
        
        negative_sentiment = db.query(Email).filter(
            Email.received_date >= today,
            Email.sentiment == 'negative'
        ).count()
        
        neutral_sentiment = db.query(Email).filter(
            Email.received_date >= today,
            Email.sentiment == 'neutral'
        ).count()
        
        emails_resolved = db.query(Email).filter(
            Email.received_date >= today,
            Email.is_responded == True
        ).count()
        
        emails_pending = db.query(Email).filter(
            Email.received_date >= today,
            Email.is_responded == False
        ).count()
        
        # Update analytics
        analytics.total_emails = total_emails
        analytics.urgent_emails = urgent_emails
        analytics.positive_sentiment = positive_sentiment
        analytics.negative_sentiment = negative_sentiment
        analytics.neutral_sentiment = neutral_sentiment
        analytics.emails_resolved = emails_resolved
        analytics.emails_pending = emails_pending
        
        db.commit()
    
    def sync_emails(self, hours_back: int = 24) -> Dict:
        """Main method to sync emails from server"""
        try:
            # Fetch emails
            emails = self.fetch_emails(hours_back)
            
            if not emails:
                return {"success": True, "message": "No new emails found", "processed": 0}
            
            # Process emails
            db = next(get_db())
            processed_count = self.process_emails(emails, db)
            
            # Update analytics
            self.update_analytics(db)
            
            return {
                "success": True,
                "message": f"Successfully processed {processed_count} emails",
                "processed": processed_count
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error syncing emails: {e}", "processed": 0}
