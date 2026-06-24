# tools.py
#Gmail MCP Tool call, Google Calendar MCP, Google Tasks

import os
from datetime import datetime, timedelta

def load_agent_prompt(filename: str = "prompt.md") -> str:
    """
    Standard utility helper (Not an LLM tool). 
    Loads the system markdown file from disk before the LLM call 
    to keep context windows lightweight.
    """
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error loading system prompt file: {str(e)}"


def get_unread_emails(last_run_timestamp: str = None) -> list:
    """
    Simulates fetching raw emails from an email provider API.
    """
    if not last_run_timestamp:
        last_run_timestamp = (datetime.now() - timedelta(hours=12)).isoformat()
        
    mock_emails = [
        {
            "id": "msg_001",
            "sender_name": "Sarah Jenkins",
            "sender_email": "sjenkins@njm.com",
            "subject": "IT Innovation Synch / Q3 Project Goals",
            "timestamp": "2026-06-24T09:15:00Z",
            "body": "Hey Jimmy, looking forward to your update on the AI insurance assistant during our synch today. Can you make sure the prompt routing doc is ready to share with the team?",
            "thread_id": "thread_abc123"
        },
        {
            "id": "msg_002",
            "sender_name": "Stripe Billing",
            "sender_email": "billing@stripe.com",
            "subject": "Invoice Paid for OpenAI API Usage",
            "timestamp": "2026-06-24T08:02:00Z",
            "body": "Your payment of $14.22 to OpenAI has been processed successfully. Invoice #INV-88329.",
            "thread_id": "thread_xyz789"
        },
        {
            "id": "msg_003",
            "sender_name": "Tech Talent Recruiter",
            "sender_email": "alex.v@stripe-careers.com",
            "subject": "Stripe Summer 2027 SWE Internship Application",
            "timestamp": "2026-06-24T10:30:00Z",
            "body": "Hi Jimmy, thanks for applying to Stripe. We reviewed your profile and want to invite you to complete our online technical assessment. Please complete it within 7 days using this link: https://stripe.com/assess/xyz",
            "thread_id": "thread_stripe99"
        },
        {
            "id": "msg_004",
            "sender_name": "Crypto Wealth Team",
            "sender_email": "noreply@spammycrypto-deals.xyz",
            "subject": "!!! URGENT: You have been selected for 500 Free Tokens !!!",
            "timestamp": "2026-06-24T11:00:00Z",
            "body": "Act now! Claim your free tokens before the deadline tonight. Click here to verify your wallet credentials.",
            "thread_id": "thread_spam01"
        }
    ]
    
    filtered_emails = [e for e in mock_emails if e["timestamp"] > last_run_timestamp]
    return filtered_emails