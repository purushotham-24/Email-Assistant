#!/usr/bin/env python3
"""
Simple Server for AI Email Assistant Demo
This server works with minimal dependencies and shows the dashboard
"""

import json
import sqlite3
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/dashboard':
            self.serve_dashboard()
        elif self.path == '/api/emails':
            self.serve_emails_api()
        elif self.path == '/api/stats':
            self.serve_stats_api()
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        """Serve the main dashboard"""
        # Read the premium HTML file
        try:
            with open("demo.html", "r", encoding="utf-8") as f:
                html_content = f.read()
        except:
            # Fallback to basic HTML if demo.html not found
            html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Email Assistant - Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #1d1d1f;
            line-height: 1.6;
            overflow-x: hidden;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 15px; }
        .header { 
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            padding: 20px;
            border-radius: 16px;
            margin-bottom: 20px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .stat-card { 
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            padding: 25px; 
            border-radius: 20px; 
            text-align: center; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        }
        .stat-number { 
            font-size: 3rem; 
            font-weight: 800;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .stat-label { color: #6e6e73; font-size: 1rem; font-weight: 500; }
        .charts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .chart-card { 
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            padding: 15px; 
            border-radius: 12px; 
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            height: 180px;
        }
        .chart-card h3 {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 10px;
            color: #1d1d1f;
        }
        .emails-section { 
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            padding: 20px; 
            border-radius: 16px; 
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .email-item { 
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 20px; 
            margin: 15px 0; 
            border-radius: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        }
        .email-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        }
        .email-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; flex-wrap: wrap; gap: 10px; }
        .priority-urgent { background: linear-gradient(135deg, #ff6b6b, #ee5a52); border-left: 4px solid #ff4757; }
        .priority-normal { background: linear-gradient(135deg, #74b9ff, #0984e3); border-left: 4px solid #74b9ff; }
        .sentiment-positive { color: #00b894; font-weight: 600; }
        .sentiment-negative { color: #e17055; font-weight: 600; }
        .sentiment-neutral { color: #636e72; font-weight: 600; }
        .status-badge { 
            padding: 6px 12px; 
            border-radius: 20px; 
            font-size: 0.75rem; 
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .status-urgent { background: linear-gradient(135deg, #ff6b6b, #ee5a52); color: white; }
        .status-normal { background: linear-gradient(135deg, #74b9ff, #0984e3); color: white; }
        .status-resolved { background: linear-gradient(135deg, #00b894, #00a085); color: white; }
        .status-pending { background: linear-gradient(135deg, #fdcb6e, #e17055); color: white; }
        .btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        }
        @media (max-width: 768px) {
            .container { padding: 15px; }
            .header { padding: 20px; text-align: center; }
            .header h1 { font-size: 2rem; }
            .stats-grid { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
            .charts-grid { grid-template-columns: 1fr; }
            .email-header { flex-direction: column; align-items: flex-start; }
            .stat-number { font-size: 2.5rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI-Powered Email Communication Assistant</h1>
            <p>Intelligent email management with AI-powered analysis and response generation</p>
            <button onclick="loadDashboard()" style="background: #059669; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 1.1em;">🔄 Refresh Dashboard</button>
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
                // Load stats
                const statsResponse = await fetch('/api/stats');
                const stats = await statsResponse.json();
                
                // Update stats
                document.getElementById('total-emails').textContent = stats.total_emails;
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
                        data: [stats.positive_sentiment, stats.negative_sentiment, stats.neutral_sentiment],
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
                        data: [stats.urgent_emails, stats.total_emails - stats.urgent_emails],
                        backgroundColor: ['#dc2626', '#2563eb']
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
        
        async function loadEmails() {
            try {
                const response = await fetch('/api/emails');
                const emails = await response.json();
                
                const emailsList = document.getElementById('emails-list');
                if (emails.length === 0) {
                    emailsList.innerHTML = '<p>No emails found.</p>';
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
        
        // Load dashboard on page load
        document.addEventListener('DOMContentLoaded', loadDashboard);
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def serve_emails_api(self):
        """Serve emails API"""
        try:
            conn = sqlite3.connect("demo_email_assistant.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM emails 
                ORDER BY 
                    CASE priority 
                        WHEN 'urgent' THEN 1 
                        ELSE 2 
                    END,
                    received_date ASC
            """)
            
            emails = cursor.fetchall()
            
            # Convert to JSON format
            email_list = []
            for email in emails:
                email_list.append({
                    "id": email[0],
                    "message_id": email[1],
                    "sender_email": email[2],
                    "subject": email[3],
                    "body": email[4],
                    "received_date": email[5],
                    "sentiment": email[6],
                    "priority": email[7],
                    "category": email[8],
                    "is_processed": bool(email[9]),
                    "is_responded": bool(email[10]),
                    "response_generated": email[11],
                    "response_sent": bool(email[12]),
                    "extracted_info": email[13]
                })
            
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(email_list).encode())
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_stats_api(self):
        """Serve statistics API"""
        try:
            conn = sqlite3.connect("demo_email_assistant.db")
            cursor = conn.cursor()
            
            # Get analytics
            cursor.execute("SELECT * FROM email_analytics ORDER BY date DESC LIMIT 1")
            analytics = cursor.fetchone()
            
            if analytics:
                stats = {
                    "total_emails": analytics[2],
                    "urgent_emails": analytics[3],
                    "positive_sentiment": analytics[4],
                    "negative_sentiment": analytics[5],
                    "neutral_sentiment": analytics[6],
                    "emails_resolved": analytics[7],
                    "emails_pending": analytics[8]
                }
            else:
                stats = {
                    "total_emails": 0,
                    "urgent_emails": 0,
                    "positive_sentiment": 0,
                    "negative_sentiment": 0,
                    "neutral_sentiment": 0,
                    "emails_resolved": 0,
                    "emails_pending": 0
                }
            
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode())
            
        except Exception as e:
            self.send_error(500, str(e))

def run_simple_server():
    """Run the simple HTTP server"""
    print("🚀 Starting AI Email Assistant - Simple Server")
    print("📍 Server will be available at: http://localhost:8080")
    print("🔄 Press Ctrl+C to stop the server")
    print("\n" + "=" * 50)
    
    # Make sure demo database exists
    if not os.path.exists("demo_email_assistant.db"):
        print("Creating demo database...")
        from simple_demo import create_demo_database
        create_demo_database()
    
    server = HTTPServer(('localhost', 8080), SimpleHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        server.shutdown()

if __name__ == "__main__":
    run_simple_server()
