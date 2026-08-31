import os 
from dotenv import load_dotenv
from langchain_core.messages import ToolMessage,AIMessage,SystemMessage
# from langchain_openrouter import ChatOpenRouter
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import MessagesState,StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import interrupt
from agent.mcp_client import create_mcp_client
from typing import Literal


load_dotenv()
NEED_REVIEW = ["close_ticket","update_ticket_priority"]


class StateSupport(MessagesState):
    review_response : Literal["approve", "reject"] | None   
    
    
def human_review(state):
    """ """
    last_message = state["messages"][-1]
    tools = [tool for tool in last_message.tool_calls if tool["name"] in NEED_REVIEW]
    answer = interrupt({
        "type": "sensitive_tool_review",
        "question": (
            "Autoriser l'exécution de cette action sensible ?"
        ),
        "tool_calls": tools,
        "allowed_decisions": [
            "approve",
            "reject",
        ],
    })
    
    
    if answer["decision"] not in ["approve", "reject"]:
        raise ValueError("La décision doit etre soit 'approve' ou 'reject' ")
    
    if answer["decision"] == "reject":
        rejection_message = [ToolMessage(content="Action annulée : l'opérateur humain a rejeté la NEEDe. ", tool_call_id = tool_call["id"],name=tool_call["name"] )for tool_call in last_message.tool_calls]
        return {"review_response":"reject", "messages":rejection_message}
    else : 
        return {"review_response": "approve"}


def condition_agent(state):
    last_message = state["messages"][-1]
    
    if not isinstance(last_message, AIMessage):
        return "end"
    if not last_message.tool_calls:
        return "end"
    
    for tool in last_message.tool_calls : 
        if tool['name'] in NEED_REVIEW:
            return "human review"
    return "tool"


def condition_human(state):
    
    if state["review_response"]=="approve":
        return "tool"
    return "agent"
    
    
async def build_graph(checkpointer = None):
    client = create_mcp_client()
    tools = await client.get_tools()
    # model = ChatOpenRouter(model= "nvidia/nemotron-3-ultra-550b-a55b:free", temperature=0, timeout=120,max_retries=3)
    model = ChatGoogleGenerativeAI(model = "gemini-3.6-flash")
    model_tools = model.bind_tools(tools)
    async def call_agent(state):
        """ """
        SYSTEM_PROMPT = """
        Tu es un agent de support technique utilisant des outils MCP.

        Règles :
        - Lorsqu'un utilisateur demande une action correspondant à un outil,
        produis immédiatement le tool call approprié.
        - Pour toute question portant sur une procédure
        ou une politique, appelle search_documentation.
        - Utilise uniquement les informations retournées
        par la documentation.
        - Mentionne les documents utilisés dans ta réponse.
        - Si la documentation ne contient pas la réponse,
        indique que tu ne disposes pas d'information fiable.
        - Lorsqu'une action correspond à un outil, produis
        le tool call approprié.
        - Ne demande jamais toi-même la confirmation d'une
        action sensible : LangGraph s'en charge.
        - Ne demande jamais toi-même la confirmation d'une action sensible.
        - Le graphe LangGraph intercepte automatiquement les outils sensibles
        et demande la validation humaine avant leur exécution.
        - Après le résultat d'un outil, formule une réponse claire.
        """
        response = await model_tools.ainvoke([SystemMessage(content=SYSTEM_PROMPT),*state["messages"]])
        return {"messages":[response]}
    
    tool = ToolNode(tools)
    
    graph = StateGraph(StateSupport)
    
    graph.add_node("agent",call_agent)
    graph.add_node("human",human_review)
    graph.add_node("tool",tool)
    
    graph.add_edge(START,"agent")
    graph.add_conditional_edges("agent",condition_agent,{"end":END,"tool":"tool","human review":"human"})
    graph.add_conditional_edges("human",condition_human,{"tool":"tool","agent":"agent"})
    graph.add_edge("tool","agent")
    if checkpointer is None :
        checkpointer = InMemorySaver()
    
    return graph.compile(checkpointer=checkpointer)