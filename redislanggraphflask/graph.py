from typing import List, TypedDict,Dict,Any
from langgraph.graph import StateGraph, START, END
import json, IPython, re
import requests
from typing_extensions import Annotated
import operator

class AgentState(TypedDict):
    text : Annotated[Dict[str, Any], operator.or_]
    process : str
    results: Annotated[Dict[str, Any], operator.or_]

def router(state: AgentState) -> AgentState:
    return state 

def route_condition(state: AgentState):

    if state["process"] == "legal_chronology":
        return "chronology_process"
    elif state["process"] == "hlss":
        return "hlss_process"
    
    
def chronology(state: AgentState) :
    res = requests.post(
        "http://localhost:9012",
        json={"text": state["text"]}
    )

    return {"results": {"chronology": res.json()}}

def hlss(state: AgentState) :
    res = requests.post(
        "http://localhost:9020",
        json={"text": state["text"]}
    )

    return {"results": {"hlss": res.json()}}

graph=StateGraph(AgentState)

graph.add_node("router",router)
graph.add_node("chronology",chronology)
graph.add_node("hlss",hlss)

graph.add_edge(START,"router")

graph.add_conditional_edges(
    "router",
    route_condition,
    {
        #Edge:Node
        "chronology_process":"chronology",
        "hlss_process":"hlss"
    }
)

graph.add_edge("chronology", END)
graph.add_edge("hlss", END)

app = graph.compile()



