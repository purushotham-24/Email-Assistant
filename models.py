from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

class EmailBase(BaseModel):
    sender_email: str
    subject: str
    body: str
    received_date: datetime

class EmailCreate(EmailBase):
    message_id: str

class EmailResponse(EmailBase):
    id: int
    message_id: str
    sentiment: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    is_processed: bool
    is_responded: bool
    response_generated: Optional[str] = None
    response_sent: bool
    extracted_info: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EmailUpdate(BaseModel):
    sentiment: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    is_processed: Optional[bool] = None
    is_responded: Optional[bool] = None
    response_generated: Optional[str] = None
    response_sent: Optional[bool] = None
    extracted_info: Optional[str] = None

class EmailFilter(BaseModel):
    sentiment: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    is_processed: Optional[bool] = None
    is_responded: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

class EmailAnalyticsResponse(BaseModel):
    total_emails: int
    urgent_emails: int
    positive_sentiment: int
    negative_sentiment: int
    neutral_sentiment: int
    emails_resolved: int
    emails_pending: int
    date: datetime

class KnowledgeBaseItem(BaseModel):
    question: str
    answer: str
    category: str

class KnowledgeBaseCreate(KnowledgeBaseItem):
    pass

class KnowledgeBaseResponse(KnowledgeBaseItem):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AIResponseRequest(BaseModel):
    email_id: int
    custom_prompt: Optional[str] = None

class AIResponseResponse(BaseModel):
    response: str
    confidence: float
    reasoning: str

class EmailProcessingRequest(BaseModel):
    email_ids: List[int]

class EmailProcessingResponse(BaseModel):
    processed_count: int
    success: bool
    message: str

class DashboardStats(BaseModel):
    total_emails_today: int
    urgent_emails: int
    emails_resolved: int
    emails_pending: int
    sentiment_distribution: Dict[str, int]
    priority_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
