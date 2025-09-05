import openai
import json
import re
from typing import Dict, List, Tuple, Optional
from config import settings
from database import KnowledgeBase
from sqlalchemy.orm import Session
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

class AIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.knowledge_base_embeddings = None
        self.knowledge_base_texts = []
        self.knowledge_base_answers = []
        
    def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of email text using OpenAI"""
        try:
            response = openai.ChatCompletion.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a sentiment analysis expert. Analyze the sentiment of the following text and respond with exactly one word: 'positive', 'negative', or 'neutral'."},
                    {"role": "user", "content": f"Analyze the sentiment of this text: {text[:1000]}"}
                ],
                max_tokens=10,
                temperature=0.1
            )
            sentiment = response.choices[0].message.content.strip().lower()
            if sentiment in ['positive', 'negative', 'neutral']:
                return sentiment
            return 'neutral'
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return 'neutral'
    
    def detect_priority(self, text: str, subject: str) -> str:
        """Detect if email is urgent based on keywords and context"""
        text_lower = (text + " " + subject).lower()
        
        # Check for urgency keywords
        urgency_score = sum(1 for keyword in settings.URGENCY_KEYWORDS if keyword in text_lower)
        
        # Check for time-sensitive indicators
        time_patterns = [
            r'\b(immediately|asap|urgent|critical)\b',
            r'\b(cannot access|broken|down|not working)\b',
            r'\b(emergency|help needed|stuck)\b'
        ]
        
        time_score = sum(len(re.findall(pattern, text_lower)) for pattern in time_patterns)
        
        # Check for emotional intensity
        emotional_words = ['frustrated', 'angry', 'desperate', 'helpless', 'urgent']
        emotional_score = sum(1 for word in emotional_words if word in text_lower)
        
        total_score = urgency_score + time_score + emotional_score
        
        if total_score >= 2:
            return 'urgent'
        return 'not_urgent'
    
    def categorize_email(self, subject: str, body: str) -> str:
        """Categorize email based on content"""
        text_lower = (subject + " " + body).lower()
        
        categories = {
            'support': ['support', 'help', 'assistance', 'issue', 'problem'],
            'query': ['question', 'inquiry', 'ask', 'wondering'],
            'request': ['request', 'need', 'want', 'require'],
            'complaint': ['complaint', 'dissatisfied', 'unhappy', 'disappointed'],
            'feedback': ['feedback', 'suggestion', 'improvement', 'review']
        }
        
        scores = {}
        for category, keywords in categories.items():
            scores[category] = sum(1 for keyword in keywords if keyword in text_lower)
        
        # Return category with highest score
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return 'general'
    
    def extract_information(self, text: str) -> Dict:
        """Extract key information from email text"""
        extracted_info = {
            'contact_details': {},
            'requirements': [],
            'sentiment_indicators': [],
            'metadata': {}
        }
        
        # Extract phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        if phones:
            extracted_info['contact_details']['phone'] = phones[0]
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            extracted_info['contact_details']['alternate_email'] = emails[0]
        
        # Extract requirements/requests
        requirement_patterns = [
            r'I need (.+?)(?:\.|$)',
            r'Please (.+?)(?:\.|$)',
            r'Can you (.+?)(?:\.|$)',
            r'I want (.+?)(?:\.|$)'
        ]
        
        for pattern in requirement_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            extracted_info['requirements'].extend(matches)
        
        # Extract sentiment indicators
        positive_words = ['happy', 'satisfied', 'great', 'excellent', 'love', 'amazing']
        negative_words = ['frustrated', 'angry', 'disappointed', 'terrible', 'hate', 'awful']
        
        for word in positive_words:
            if word in text.lower():
                extracted_info['sentiment_indicators'].append(f'positive: {word}')
        
        for word in negative_words:
            if word in text.lower():
                extracted_info['sentiment_indicators'].append(f'negative: {word}')
        
        return extracted_info
    
    def build_knowledge_base_index(self, db: Session):
        """Build FAISS index for knowledge base RAG"""
        knowledge_items = db.query(KnowledgeBase).all()
        
        if not knowledge_items:
            return
        
        texts = [f"{item.question} {item.answer}" for item in knowledge_items]
        embeddings = self.model.encode(texts)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.knowledge_base_index = faiss.IndexFlatL2(dimension)
        self.knowledge_base_index.add(embeddings.astype('float32'))
        
        self.knowledge_base_texts = texts
        self.knowledge_base_answers = [item.answer for item in knowledge_items]
    
    def retrieve_relevant_context(self, query: str, top_k: int = 3) -> List[str]:
        """Retrieve relevant context from knowledge base using RAG"""
        if not hasattr(self, 'knowledge_base_index') or self.knowledge_base_index is None:
            return []
        
        query_embedding = self.model.encode([query])
        D, I = self.knowledge_base_index.search(query_embedding.astype('float32'), top_k)
        
        relevant_contexts = []
        for idx in I[0]:
            if idx < len(self.knowledge_base_answers):
                relevant_contexts.append(self.knowledge_base_answers[idx])
        
        return relevant_contexts
    
    def generate_response(self, email_text: str, email_subject: str, sender_email: str, 
                         sentiment: str, priority: str, category: str, 
                         custom_prompt: str = None) -> Tuple[str, float, str]:
        """Generate AI-powered response using RAG and context-aware prompting"""
        
        # Retrieve relevant context from knowledge base
        relevant_context = self.retrieve_relevant_context(email_text)
        context_text = "\n".join(relevant_context) if relevant_context else "No specific knowledge base context available."
        
        # Build system prompt with context
        system_prompt = f"""You are a professional customer support AI assistant. Your role is to:
1. Generate empathetic, helpful, and professional responses
2. Use the provided knowledge base context when relevant
3. Acknowledge the customer's sentiment and priority level
4. Provide clear, actionable solutions
5. Maintain a friendly and professional tone

Knowledge Base Context:
{context_text}

Email Category: {category}
Priority Level: {priority}
Sentiment: {sentiment}

Guidelines:
- If sentiment is negative, acknowledge their frustration empathetically
- If priority is urgent, emphasize quick resolution
- Use the knowledge base context when it's relevant to their query
- Be specific and actionable in your response
- Keep the tone professional yet warm
- If you don't have enough information, ask clarifying questions"""

        # Build user prompt
        user_prompt = f"""Generate a response to this email:

From: {sender_email}
Subject: {email_subject}
Content: {email_text}

{f"Additional Instructions: {custom_prompt}" if custom_prompt else ""}

Please provide a professional, empathetic response that addresses their needs."""

        try:
            response = openai.ChatCompletion.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            generated_response = response.choices[0].message.content.strip()
            
            # Calculate confidence based on response length and relevance
            confidence = min(0.9, len(generated_response) / 100)
            
            reasoning = f"Generated response for {category} email with {sentiment} sentiment and {priority} priority. Used {len(relevant_context)} relevant knowledge base items."
            
            return generated_response, confidence, reasoning
            
        except Exception as e:
            print(f"Error generating response: {e}")
            fallback_response = f"Thank you for your {category} request. I understand this is {priority} priority. I'm currently processing your inquiry and will get back to you shortly with a detailed response."
            return fallback_response, 0.5, "Fallback response due to AI service error"
    
    def update_knowledge_base(self, question: str, answer: str, category: str, db: Session):
        """Add new knowledge base item and update index"""
        new_item = KnowledgeBase(
            question=question,
            answer=answer,
            category=category
        )
        db.add(new_item)
        db.commit()
        
        # Rebuild index
        self.build_knowledge_base_index(db)
