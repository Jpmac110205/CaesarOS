# agent.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, ToolMessage
from tools import load_agent_prompt, query_prodigy_rag

load_dotenv()

def run_tutoring_session(user_question: str) -> str:
    """
    Executes a LangChain invocation that binds local tools, reads 
    the system prompt dynamically from storage, and executes the conversation loop.
    """
    # 1. Dynamically load the specific 200-line markdown prompt
    system_instruction = load_agent_prompt("tutoring_prompt.md")
    
    # 2. Build standard LangChain prompt template
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_instruction),
        ("placeholder", "{messages}")
    ])
    
    # 3. Initialize the model and bind native tools
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3
    )
    
    # Define our available tool array and bind it to the model
    tools_list = [query_prodigy_rag]
    llm_with_tools = llm.bind_tools(tools_list)
    
    # Compile the prompt chain setup
    chain = prompt_template | llm_with_tools
    
    # 4. Initialize message state with user query
    messages_state = [HumanMessage(content=user_question)]
    
    # First invocation to let the model decide if it needs the Prodigy Tool
    response = chain.invoke({"messages": messages_state})
    
    # 5. Handle Tool Calling Loop if the model requested data access
    if response.tool_calls:
        messages_state.append(response) # Add model's tool request to history
        
        for tool_call in response.tool_calls:
            if tool_call["name"] == "query_prodigy_rag":
                # Execute the native python tool function directly
                tool_output = query_prodigy_rag.invoke(tool_call["args"])
                
                # Append the result back to history matching LangChain specs
                messages_state.append(
                    ToolMessage(content=str(tool_output), tool_call_id=tool_call["id"])
                )
        
        # Second invocation: Give the model the tool results so it can output the final formatted answer
        final_response = chain.invoke({"messages": messages_state})
        return final_response.content

    return response.content

if __name__ == "__main__":
    print("--- Activating Sage (LangChain Version) ---")
    question = "I don't really get how attention works in transformers—I know it's important but the math loses me"
    
    explanation = run_tutoring_session(question)
    print(explanation)