from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime, timedelta

from database import get_db, Email, EmailAnalytics, KnowledgeBase
from models import (
    EmailResponse, EmailUpdate, EmailFilter, EmailAnalyticsResponse,
    KnowledgeBaseCreate, KnowledgeBaseResponse, AIResponseRequest,
    AIResponseResponse, EmailProcessingRequest, EmailProcessingResponse,
    DashboardStats
)
from email_service import EmailService
from ai_service import AIService

app = FastAPI(
    title="AI-Powered Email Communication Assistant",
    description="Intelligent email management system with AI-powered analysis and response generation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
email_service = EmailService()
ai_service = AIService()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main dashboard"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Email Assistant</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
            .stat-card { background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .stat-number { font-size: 2em; font-weight: bold; color: #2563eb; }
            .stat-label { color: #6b7280; margin-top: 5px; }
            .charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
            .chart-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .emails-section { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .email-item { border: 1px solid #e5e7eb; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .email-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
            .priority-urgent { background: #fef2f2; border-left: 4px solid #dc2626; }
            .priority-normal { background: #f0f9ff; border-left: 4px solid #2563eb; }
            .sentiment-positive { color: #059669; }
            .sentiment-negative { color: #dc2626; }
            .sentiment-neutral { color: #6b7280; }
            .btn { background: #2563eb; color: white; padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
            .btn:hover { background: #1d4ed8; }
            .btn-secondary { background: #6b7280; }
            .btn-secondary:hover { background: #4b5563; }
            .sync-btn { background: #059669; font-size: 1.1em; padding: 12px 24px; }
            .sync-btn:hover { background: #047857; }
            .btn-success { background: #059669; }
            .btn-success:hover { background: #047857; }
            .btn-danger { background: #dc2626; }
            .btn-danger:hover { background: #b91c1c; }
            .email-actions { display: flex; gap: 10px; flex-wrap: wrap; }
            .status-badge { padding: 4px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }
            .status-urgent { background: #fef2f2; color: #dc2626; }
            .status-normal { background: #f0f9ff; color: #2563eb; }
            .status-resolved { background: #f0fdf4; color: #059669; }
            .status-pending { background: #fffbeb; color: #d97706; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 AI-Powered Email Communication Assistant</h1>
                <p>Intelligent email management with AI-powered analysis and response generation</p>
                <button class="btn sync-btn" onclick="syncEmails()">🔄 Sync Emails</button>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number" id="total-emails">-</div>
                    <div class="stat-label">Total Emails Today</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="urgent-emails">-</div>
                    <div class="stat-label">Urgent Emails</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="emails-resolved">-</div>
                    <div class="stat-label">Emails Resolved</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="emails-pending">-</div>
                    <div class="stat-label">Emails Pending</div>
                </div>
            </div>
            
            <div class="charts-grid">
                <div class="chart-card">
                    <h3>Sentiment Distribution</h3>
                    <canvas id="sentimentChart"></canvas>
                </div>
                <div class="chart-card">
                    <h3>Priority Distribution</h3>
                    <canvas id="priorityChart"></canvas>
                </div>
            </div>
            
            <div class="emails-section">
                <h3>📧 Support Emails (Priority Order)</h3>
                <div id="emails-list">Loading emails...</div>
            </div>
        </div>
        
        <script>
            let sentimentChart, priorityChart;
            
            async function loadDashboard() {
                try {
                    const response = await fetch('/api/dashboard/stats');
                    const stats = await response.json();
                    
                    // Update stats
                    document.getElementById('total-emails').textContent = stats.total_emails_today;
                    document.getElementById('urgent-emails').textContent = stats.urgent_emails;
                    document.getElementById('emails-resolved').textContent = stats.emails_resolved;
                    document.getElementById('emails-pending').textContent = stats.emails_pending;
                    
                    // Update charts
                    updateCharts(stats);
                    
                    // Load emails
                    loadEmails();
                    
                } catch (error) {
                    console.error('Error loading dashboard:', error);
                }
            }
            
            function updateCharts(stats) {
                // Sentiment Chart
                const sentimentCtx = document.getElementById('sentimentChart').getContext('2d');
                if (sentimentChart) sentimentChart.destroy();
                
                sentimentChart = new Chart(sentimentCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Positive', 'Negative', 'Neutral'],
                        datasets: [{
                            data: [stats.sentiment_distribution.positive, stats.sentiment_distribution.negative, stats.sentiment_distribution.neutral],
                            backgroundColor: ['#10b981', '#ef4444', '#6b7280']
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false }
                });
                
                // Priority Chart
                const priorityCtx = document.getElementById('priorityChart').getContext('2d');
                if (priorityChart) priorityChart.destroy();
                
                priorityChart = new Chart(priorityCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Urgent', 'Not Urgent'],
                        datasets: [{
                            data: [stats.priority_distribution.urgent, stats.priority_distribution.not_urgent],
                            backgroundColor: ['#dc2626', '#2563eb']
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false }
                });
            }
            
            async function loadEmails() {
                try {
                    const response = await fetch('/api/emails/priority-queue');
                    const emails = await response.json();
                    
                    const emailsList = document.getElementById('emails-list');
                    if (emails.length === 0) {
                        emailsList.innerHTML = '<p>No pending emails found.</p>';
                        return;
                    }
                    
                    emailsList.innerHTML = emails.map(email => `
                        <div class="email-item ${email.priority === 'urgent' ? 'priority-urgent' : 'priority-normal'}">
                            <div class="email-header">
                                <div>
                                    <strong>${email.subject}</strong>
                                    <br>
                                    <small>From: ${email.sender_email}</small>
                                    <br>
                                    <small>Received: ${new Date(email.received_date).toLocaleString()}</small>
                                </div>
                                <div style="text-align: right;">
                                    <div class="status-badge ${email.priority === 'urgent' ? 'status-urgent' : 'status-normal'}">
                                        ${email.priority === 'urgent' ? '🚨 URGENT' : '📧 NORMAL'}
                                    </div>
                                    <br>
                                    <span class="sentiment-${email.sentiment}">${email.sentiment.toUpperCase()}</span>
                                    <br>
                                    <span class="status-badge ${email.is_responded ? 'status-resolved' : 'status-pending'}">
                                        ${email.is_responded ? '✅ RESOLVED' : '⏳ PENDING'}
                                    </span>
                                    <br>
                                    <span>${email.category}</span>
                                </div>
                            </div>
                            <div style="margin: 10px 0;">
                                <strong>Body:</strong> ${email.body.substring(0, 200)}${email.body.length > 200 ? '...' : ''}
                            </div>
                            <div class="email-actions">
                                <button class="btn" onclick="generateResponse(${email.id})">🤖 Generate AI Response</button>
                                <button class="btn btn-secondary" onclick="viewEmail(${email.id})">👁️ View Details</button>
                                ${email.response_generated ? `
                                    <button class="btn btn-success" onclick="sendResponse(${email.id})">📤 Send Response</button>
                                ` : ''}
                            </div>
                            ${email.response_generated ? `
                                <div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 5px;">
                                    <strong>AI Response:</strong>
                                    <div style="margin-top: 5px; font-style: italic;">${email.response_generated.substring(0, 200)}${email.response_generated.length > 200 ? '...' : ''}</div>
                                </div>
                            ` : ''}
                        </div>
                    `).join('');
                    
                } catch (error) {
                    console.error('Error loading emails:', error);
                    document.getElementById('emails-list').innerHTML = '<p>Error loading emails.</p>';
                }
            }
            
            async function syncEmails() {
                const btn = event.target;
                btn.disabled = true;
                btn.textContent = '🔄 Syncing...';
                
                try {
                    const response = await fetch('/api/emails/sync', { method: 'POST' });
                    const result = await response.json();
                    
                    if (result.success) {
                        alert(`✅ ${result.message}`);
                        loadDashboard();
                    } else {
                        alert(`❌ ${result.message}`);
                    }
                } catch (error) {
                    alert('❌ Error syncing emails');
                    console.error('Error:', error);
                } finally {
                    btn.disabled = false;
                    btn.textContent = '🔄 Sync Emails';
                }
            }
            
            async function generateResponse(emailId) {
                try {
                    const response = await fetch(`/api/emails/${emailId}/generate-response`, { method: 'POST' });
                    const result = await response.json();
                    
                    if (result.response) {
                        alert('🤖 AI Response Generated!\n\n' + result.response.substring(0, 200) + '...');
                        loadEmails();
                    } else {
                        alert('❌ Error generating response');
                    }
                } catch (error) {
                    alert('❌ Error generating response');
                    console.error('Error:', error);
                }
            }
            
            function viewEmail(emailId) {
                // In a real app, this would open a modal or navigate to a detailed view
                alert('View email details - Feature to be implemented');
            }
            
            async function sendResponse(emailId) {
                if (!confirm('Are you sure you want to send the AI-generated response?')) {
                    return;
                }
                
                try {
                    const response = await fetch(`/api/emails/${emailId}/send-response`, { method: 'POST' });
                    const result = await response.json();
                    
                    if (response.ok) {
                        alert('✅ Email response sent successfully!');
                        loadEmails();
                        loadDashboard();
                    } else {
                        alert('❌ Error sending response: ' + result.detail);
                    }
                } catch (error) {
                    alert('❌ Error sending response');
                    console.error('Error:', error);
                }
            }
            
            // Load dashboard on page load
            document.addEventListener('DOMContentLoaded', loadDashboard);
        </script>
    </body>
    </html>
    """

# API Endpoints

@app.get("/api/emails/", response_model=List[EmailResponse])
async def get_emails(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all emails with pagination"""
    emails = db.query(Email).offset(skip).limit(limit).all()
    return emails

@app.get("/api/emails/{email_id}", response_model=EmailResponse)
async def get_email(email_id: int, db: Session = Depends(get_db)):
    """Get a specific email by ID"""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email

@app.get("/api/emails/priority-queue", response_model=List[EmailResponse])
async def get_priority_queue(db: Session = Depends(get_db)):
    """Get emails in priority order (urgent first)"""
    return email_service.get_priority_queue(db)

@app.post("/api/emails/sync")
async def sync_emails(background_tasks: BackgroundTasks):
    """Sync emails from email server"""
    try:
        result = email_service.sync_emails()
        return result
    except Exception as e:
        return {"success": False, "message": f"Error syncing emails: {e}", "processed": 0}

@app.post("/api/emails/{email_id}/generate-response", response_model=AIResponseResponse)
async def generate_ai_response(
    email_id: int,
    request: AIResponseRequest,
    db: Session = Depends(get_db)
):
    """Generate AI response for an email"""
    response = email_service.generate_ai_response(
        email_id, 
        request.custom_prompt, 
        db
    )
    
    if not response:
        raise HTTPException(status_code=404, detail="Email not found or error generating response")
    
    return AIResponseResponse(
        response=response,
        confidence=0.85,
        reasoning="AI response generated successfully"
    )

@app.post("/api/emails/{email_id}/send-response")
async def send_email_response(
    email_id: int,
    custom_response: str = None,
    db: Session = Depends(get_db)
):
    """Send email response to customer"""
    success = email_service.send_email_response(email_id, custom_response, db)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send email response")
    
    return {"message": "Email response sent successfully"}

@app.put("/api/emails/{email_id}", response_model=EmailResponse)
async def update_email(
    email_id: int,
    email_update: EmailUpdate,
    db: Session = Depends(get_db)
):
    """Update email details"""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    for field, value in email_update.dict(exclude_unset=True).items():
        setattr(email, field, value)
    
    db.commit()
    db.refresh(email)
    return email

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    today = datetime.now().date()
    
    # Get today's analytics
    analytics = db.query(EmailAnalytics).filter(
        EmailAnalytics.date >= today
    ).first()
    
    if not analytics:
        # Create default analytics
        analytics = EmailAnalytics(
            date=today,
            total_emails=0,
            urgent_emails=0,
            positive_sentiment=0,
            negative_sentiment=0,
            neutral_sentiment=0,
            emails_resolved=0,
            emails_pending=0
        )
        db.add(analytics)
        db.commit()
    
    # Get distribution data
    sentiment_distribution = {
        'positive': db.query(Email).filter(
            Email.received_date >= today,
            Email.sentiment == 'positive'
        ).count(),
        'negative': db.query(Email).filter(
            Email.received_date >= today,
            Email.sentiment == 'negative'
        ).count(),
        'neutral': db.query(Email).filter(
            Email.received_date >= today,
            Email.sentiment == 'neutral'
        ).count()
    }
    
    priority_distribution = {
        'urgent': db.query(Email).filter(
            Email.received_date >= today,
            Email.priority == 'urgent'
        ).count(),
        'not_urgent': db.query(Email).filter(
            Email.received_date >= today,
            Email.priority == 'not_urgent'
        ).count()
    }
    
    category_distribution = {}
    categories = db.query(Email.category).filter(Email.received_date >= today).distinct()
    for cat in categories:
        category_distribution[cat[0]] = db.query(Email).filter(
            Email.received_date >= today,
            Email.category == cat[0]
        ).count()
    
    return DashboardStats(
        total_emails_today=analytics.total_emails,
        urgent_emails=analytics.urgent_emails,
        emails_resolved=analytics.emails_resolved,
        emails_pending=analytics.emails_pending,
        sentiment_distribution=sentiment_distribution,
        priority_distribution=priority_distribution,
        category_distribution=category_distribution
    )

@app.get("/api/knowledge-base/", response_model=List[KnowledgeBaseResponse])
async def get_knowledge_base(db: Session = Depends(get_db)):
    """Get all knowledge base items"""
    items = db.query(KnowledgeBase).all()
    return items

@app.post("/api/knowledge-base/", response_model=KnowledgeBaseResponse)
async def create_knowledge_base_item(
    item: KnowledgeBaseCreate,
    db: Session = Depends(get_db)
):
    """Create new knowledge base item"""
    db_item = KnowledgeBase(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # Update AI service knowledge base index
    ai_service.build_knowledge_base_index(db)
    
    return db_item

@app.delete("/api/knowledge-base/{item_id}")
async def delete_knowledge_base_item(item_id: int, db: Session = Depends(get_db)):
    """Delete knowledge base item"""
    item = db.query(KnowledgeBase).filter(KnowledgeBase.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Knowledge base item not found")
    
    db.delete(item)
    db.commit()
    
    # Update AI service knowledge base index
    ai_service.build_knowledge_base_index(db)
    
    return {"message": "Knowledge base item deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
