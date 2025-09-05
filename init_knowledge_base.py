#!/usr/bin/env python3
"""
Initialize Knowledge Base with Sample Data
This script populates the knowledge base with sample support information
that will be used by the RAG system for generating contextual responses.
"""

import asyncio
from database import get_db, KnowledgeBase
from ai_service import AIService
from sqlalchemy.orm import Session

def init_knowledge_base():
    """Initialize knowledge base with sample data"""
    db = next(get_db())
    ai_service = AIService()
    
    # Sample knowledge base items
    knowledge_items = [
        {
            "question": "How do I reset my password?",
            "answer": "To reset your password, please visit our password reset page at https://example.com/reset-password. Enter your email address and follow the instructions sent to your email. If you don't receive the email within 10 minutes, check your spam folder.",
            "category": "support"
        },
        {
            "question": "I can't access my account",
            "answer": "If you're unable to access your account, please try the following steps: 1) Clear your browser cache and cookies, 2) Try a different browser, 3) Check if your account is locked due to multiple failed login attempts. If the issue persists, contact our support team with your username and the specific error message you're seeing.",
            "category": "support"
        },
        {
            "question": "How do I update my billing information?",
            "answer": "To update your billing information, log into your account and navigate to Settings > Billing. You can update your credit card details, billing address, and payment method. All changes are applied immediately and will be reflected in your next billing cycle.",
            "category": "billing"
        },
        {
            "question": "What are your business hours?",
            "answer": "Our customer support team is available Monday through Friday, 9:00 AM to 6:00 PM EST. For urgent technical issues, we provide 24/7 emergency support. You can also submit support tickets at any time through our website, and we'll respond within 4 business hours.",
            "category": "general"
        },
        {
            "question": "How do I cancel my subscription?",
            "answer": "To cancel your subscription, go to your account settings and select 'Subscription Management'. Click on 'Cancel Subscription' and follow the confirmation process. Your service will remain active until the end of your current billing period. You can reactivate your subscription at any time.",
            "category": "billing"
        },
        {
            "question": "I'm experiencing slow performance",
            "answer": "If you're experiencing slow performance, please try: 1) Refreshing your browser, 2) Closing unnecessary browser tabs, 3) Checking your internet connection speed, 4) Clearing browser cache. If the issue continues, please provide details about your browser, operating system, and the specific actions that are slow.",
            "category": "technical"
        },
        {
            "question": "How do I contact customer support?",
            "answer": "You can contact our customer support team through multiple channels: 1) Email: support@example.com, 2) Phone: 1-800-SUPPORT (available during business hours), 3) Live chat on our website, 4) Support ticket system. For the fastest response, we recommend using our support ticket system.",
            "category": "general"
        },
        {
            "question": "What payment methods do you accept?",
            "answer": "We accept all major credit cards (Visa, MasterCard, American Express, Discover), PayPal, and bank transfers for annual plans. All payments are processed securely through our PCI-compliant payment processor. We also offer flexible payment plans for enterprise customers.",
            "category": "billing"
        },
        {
            "question": "How do I export my data?",
            "answer": "To export your data, go to Settings > Data Management > Export Data. You can choose to export all data or select specific data types. Exports are available in CSV, JSON, and Excel formats. Large exports may take up to 24 hours to process and will be sent to your email.",
            "category": "data"
        },
        {
            "question": "I found a bug in your system",
            "answer": "Thank you for reporting this issue. Please provide as much detail as possible including: 1) Steps to reproduce the bug, 2) Your browser and operating system, 3) Screenshots if applicable, 4) Expected vs. actual behavior. We take all bug reports seriously and will investigate promptly.",
            "category": "technical"
        },
        {
            "question": "How do I add team members to my account?",
            "answer": "To add team members, go to Settings > Team Management > Add Member. Enter their email address and select their role (Admin, Editor, or Viewer). They'll receive an invitation email with instructions to join. You can manage permissions and remove team members at any time.",
            "category": "account"
        },
        {
            "question": "What is your refund policy?",
            "answer": "We offer a 30-day money-back guarantee for all new subscriptions. If you're not satisfied with our service within the first 30 days, contact our support team for a full refund. After 30 days, refunds are evaluated on a case-by-case basis for technical issues or service failures.",
            "category": "billing"
        },
        {
            "question": "How do I enable two-factor authentication?",
            "answer": "To enable two-factor authentication, go to Settings > Security > Two-Factor Authentication. Click 'Enable 2FA' and follow the setup process. You'll need to scan a QR code with your authenticator app (Google Authenticator, Authy, etc.) and enter the verification code. We strongly recommend enabling 2FA for enhanced security.",
            "category": "security"
        },
        {
            "question": "I'm locked out of my account",
            "answer": "If you're locked out of your account due to multiple failed login attempts, please wait 15 minutes before trying again. If you still can't access your account, use the 'Forgot Password' link to reset your password. For security reasons, we may require additional verification if suspicious activity is detected.",
            "category": "security"
        },
        {
            "question": "How do I change my email address?",
            "answer": "To change your email address, go to Settings > Profile > Email Address. Enter your new email address and current password. You'll receive a verification email at the new address. Click the verification link to confirm the change. Your old email address will no longer have access to the account.",
            "category": "account"
        }
    ]
    
    print("Initializing knowledge base...")
    
    # Check if knowledge base already has items
    existing_count = db.query(KnowledgeBase).count()
    if existing_count > 0:
        print(f"Knowledge base already has {existing_count} items. Skipping initialization.")
        return
    
    # Add knowledge base items
    for item in knowledge_items:
        kb_item = KnowledgeBase(
            question=item["question"],
            answer=item["answer"],
            category=item["category"]
        )
        db.add(kb_item)
        print(f"Added: {item['question'][:50]}...")
    
    try:
        db.commit()
        print(f"Successfully added {len(knowledge_items)} knowledge base items.")
        
        # Build the FAISS index for RAG
        print("Building AI knowledge base index...")
        ai_service.build_knowledge_base_index(db)
        print("Knowledge base index built successfully!")
        
    except Exception as e:
        print(f"Error initializing knowledge base: {e}")
        db.rollback()

if __name__ == "__main__":
    init_knowledge_base()
    print("Knowledge base initialization complete!")


