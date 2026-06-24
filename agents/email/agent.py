# agent.py
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from tools import get_unread_emails, load_agent_prompt

load_dotenv()

def run_inbox_agent(time_of_day: str = "MORNING") -> str:
    """
    Executes the Inbox agent using LangChain components. Loads rules dynamically,
    batches raw email payloads, and enforces deterministic formatting.
    """
    current_time_str = datetime.now().strftime("%Y-%m-%d at %I:%M %p")
    
    # 1. Dynamically load the system prompt file from disk
    system_instruction = load_agent_prompt("prompt.md")
    
    # 2. Pull data using your utility function
    last_run = (datetime.now() - timedelta(hours=4)).isoformat()
    raw_emails = get_unread_emails(last_run_timestamp=last_run)
    
    if not raw_emails:
        return f"📬 No new emails since last digest window. Inbox is clear."
        
    # 3. Format the data payload
    user_payload = {
        "run_metadata": {
            "requested_digest": time_of_day,
            "current_time": current_time_str,
            "total_fetched": len(raw_emails)
        },
        "emails": raw_emails
    }
    
    # 4. Construct the LangChain Prompt and Chain pipeline
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_instruction),
        ("human", "Analyze and digest the following email data:\n\n{email_data}")
    ])
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.1  # Matches your original low temperature requirement for strict formatting
    )
    
    # Build the chain
    chain = prompt_template | llm
    
    # 5. Invoke the chain safely
    try:
        response = chain.invoke({
            "email_data": json.dumps(user_payload, indent=2)
        })
        return response.content
        
    except Exception as e:
        # Edge case error handler formatting specified by system prompt
        error_msg = f"⚠️ Email digest failed to run at {current_time_str}. Check connection or permissions. Error: {str(e)}"
        return error_msg

if __name__ == "__main__":
    print("--- Running Inbox Agent (LangChain Version) ---")
    digest = run_inbox_agent(time_of_day="AFTERNOON")
    print(digest)