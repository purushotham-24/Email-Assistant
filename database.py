from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
import aiosqlite
from config import settings

Base = declarative_base()

class Email(Base):
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True)
    sender_email = Column(String, index=True)
    subject = Column(String, index=True)
    body = Column(Text)
    received_date = Column(DateTime, default=datetime.utcnow)
    sentiment = Column(String)  # positive, negative, neutral
    priority = Column(String)  # urgent, not_urgent
    category = Column(String)  # support, query, request, help
    is_processed = Column(Boolean, default=False)
    is_responded = Column(Boolean, default=False)
    response_generated = Column(Text)
    response_sent = Column(Boolean, default=False)
    extracted_info = Column(Text)  # JSON string of extracted information
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class EmailAnalytics(Base):
    __tablename__ = "email_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    total_emails = Column(Integer, default=0)
    urgent_emails = Column(Integer, default=0)
    positive_sentiment = Column(Integer, default=0)
    negative_sentiment = Column(Integer, default=0)
    neutral_sentiment = Column(Integer, default=0)
    emails_resolved = Column(Integer, default=0)
    emails_pending = Column(Integer, default=0)

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, index=True)
    answer = Column(Text)
    category = Column(String, index=True)
    embedding = Column(Text)  # Vector embedding for RAG
    created_at = Column(DateTime, default=func.now())

# Database engine and session
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    async with aiosqlite.connect(settings.DATABASE_URL.replace("sqlite:///", "")) as db:
        yield db
