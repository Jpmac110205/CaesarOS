# tools.py
#TOOLS: Web search, Prodigy document database
import os
from langchain_core.tools import tool

def load_agent_prompt(filename: str = "tutoring_prompt.md") -> str:
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
        return f"Error loading tutoring prompt file: {str(e)}"


@tool
def query_prodigy_rag(search_query: str) -> str:
    """
    Queries the local Prodigy database via semantic search to retrieve 
    Jimmy's personal project notes, codebases, and saved references.
    """
    q = search_query.lower()
    
    # Mock vector store database
    mock_vector_db = [
        {
            "title": "NJM RAG Production Logs - Chunking Strategy",
            "content": "Implemented recursive character text chunking with a 500 token window and 50 token overlap. Metadata tagging includes 'department: IT-Innovation' and 'policy_type'. Benchmarked on AWS Bedrock using Claude 3.5 Sonnet and Titan Embeddings.",
            "keywords": ["rag", "embedding", "chunking", "bedrock", "njm", "semantic"]
        },
        {
            "title": "Prodigy Core Architecture Notes",
            "content": "Prodigy utilizes FastAPI + PostgreSQL backend with a React frontend. Implemented OAuth2 flow for Google Calendar and Tasks integration to sync Jimmy's scheduling data dynamically.",
            "keywords": ["prodigy", "oauth2", "fastapi", "postgres", "calendar"]
        },
        {
            "title": "NeetCode Study Guide - Sliding Window",
            "content": "Sliding window problems usually track an array subarray using left/right pointers. Key invariant: expand right pointer until constraint breaks, then shrink left pointer until constraint is met again. Time complexity linear O(n).",
            "keywords": ["sliding window", "pointer", "neetcode", "leetcode", "algorithm"]
        }
    ]
    
    for document in mock_vector_db:
        if any(keyword in q for keyword in document["keywords"]):
            return (
                f"FOUND MATCH IN PRODIGY KB:\n"
                f"Title: {document['title']}\n"
                f"Content: {document['content']}"
            )
            
    return "No matching documents found in the Prodigy knowledge base."