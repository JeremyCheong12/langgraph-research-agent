import os
import operator
import sys
from typing import Annotated, List, TypedDict

# Langchain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langgraph.graph import StateGraph, END

# Config
# NOTE: User must set their own API key here
os.environ["GOOGLE_API_KEY"] = "PASTE_YOUR_KEY_HERE"

# Global tools
ddg = DuckDuckGoSearchRun()
wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=500))

# Basic state for the graph
class ResearchState(TypedDict):
    topic: str
    pending_steps: List[str]
    results: Annotated[List[str], operator.add]
    final_out: str

def generate_plan(state: ResearchState):
    q = state['topic']
    print(f"DEBUG: generating plan for {q}...")
    
    # Using flash model since it's faster/free
    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0)
    
    # minimal prompt to get list
    msg = f"Plan 3 search queries for: {q}. Return queries on new lines only."
    res = llm.invoke(msg)
    
    # cleanup response
    raw_text = res.content
    if isinstance(raw_text, list):
        raw_text = "\n".join([str(x) for x in raw_text])
        
    # split and filter empty lines
    steps = [s.strip() for s in raw_text.split('\n') if len(s.strip()) > 2]
    return {"pending_steps": steps}

def perform_research(state: ResearchState):
    steps = state.get("pending_steps", [])
    if not steps:
        return {"results": []}

    # pop first item
    curr_query = steps[0]
    remaining = steps[1:]
    
    print(f" > executing: {curr_query}")
    
    out_data = ""
    source_tag = ""

    try:
        # crude routing check
        if "history" in curr_query.lower() or "define" in curr_query.lower():
            out_data = wiki.run(curr_query)
            source_tag = "[WIKI]"
        else:
            out_data = ddg.run(curr_query)
            source_tag = "[WEB]"
            
    except Exception as e:
        # just log it and move on, don't crash the agent
        print(f"WARN: tool failure on {curr_query} -> {e}")
        out_data = "lookup_failed"
        source_tag = "[ERR]"

    log_entry = f"{source_tag} Q: {curr_query} \n A: {out_data}\n"
    
    return {
        "results": [log_entry],
        "pending_steps": remaining
    }

def summarize(state: ResearchState):
    print("DEBUG: summarizing findings...")
    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.7)
    
    # join all previous logs
    ctx = "\n".join(state["results"])
    
    prompt = f"""
    Context:
    {ctx}
    
    Question: {state['topic']}
    
    Please answer the question using the context provided. Keep it short.
    """
    
    res = llm.invoke(prompt)
    
    # handle weird list return type from gemini
    ans = res.content
    if isinstance(ans, list):
        ans = " ".join([str(x) for x in ans])
        
    return {"final_out": ans}

def route_next(state: ResearchState):
    if len(state["pending_steps"]) > 0:
        return "loop"
    return "finish"

# Graph setup
g = StateGraph(ResearchState)

g.add_node("planner", generate_plan)
g.add_node("worker", perform_research)
g.add_node("writer", summarize)

g.set_entry_point("planner")
g.add_edge("planner", "worker")

g.add_conditional_edges(
    "worker",
    route_next,
    {
        "loop": "worker",
        "finish": "writer"
    }
)
g.add_edge("writer", END)

app = g.compile()

# Manual test run
if __name__ == "__main__":
    if len(sys.argv) > 1:
        topic = sys.argv[1]
    else:
        topic = input("Enter a topic: ")

    print(f"Starting run for: {topic}")
    
    try:
        inputs = {"topic": topic, "results": []}
        # simple invocation
        output = app.invoke(inputs)
        
        print("\n" + "-"*30)
        print(output.get("final_out", "No result"))
        print("-" * 30)
        
    except Exception as err:
        print("CRITICAL FAIL:")
        print(err)