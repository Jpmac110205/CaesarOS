import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, ToolMessage
from tools import load_agent_prompt, get_weather, get_news, get_calendar_events, get_tasks

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from assets.agentstate import AgentState


load_dotenv()

def run_planner_session(user_question: str) -> str:
    """
    Executes a LangChain invocation that binds local tools, reads 
    the system prompt dynamically from storage, and executes the conversation loop.
    """
    # 1. Dynamically load the specific 200-line markdown prompt
    system_instruction = load_agent_prompt("prompt.md")
    
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
    tools_list = [get_weather, get_news, get_calendar_events, get_tasks]
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
        final_output = ""
        #TODO: Implement a loop to handle multiple tool calls if needed
        for tool_call in response.tool_calls:
            if tool_call["name"] == "get_weather":
                # Execute the native python tool function directly
                final_output += get_weather.invoke(tool_call["args"])
            elif tool_call["name"] == "get_news":
                final_output += get_news.invoke(tool_call["args"])
            elif tool_call["name"] == "get_calendar_events":
                final_output += get_calendar_events.invoke(tool_call["args"])
            elif tool_call["name"] == "get_tasks":
                final_output += get_tasks.invoke(tool_call["args"])
        
        # Second invocation: Give the model the tool results so it can output the final formatted answer
        final_response = chain.invoke({"messages": messages_state + [ToolMessage(content=final_output, tool_call_id=tool_call["id"])]})
        AgentState.planner_output += final_response.content
        return final_response.content
    AgentState.planner_output += response.content
    return response.content

if __name__ == "__main__":
    print("--- Activating Caesar (LangChain Version) ---")
    question = "explain what a kernel is in OS"
    
    explanation = run_planner_session(question)
    print(explanation)