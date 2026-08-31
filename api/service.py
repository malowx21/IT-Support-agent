from uuid import uuid4

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from agent.graph import build_graph
from api.schemas import AgentResponse,ChatRequest, ReviewRequest

class AgentService :
    
    def __init__(self, graph):
        self.graph = graph
        
    @classmethod
    async def create(cls,checkpointer=None):
        graph = await build_graph(checkpointer=checkpointer)
        return cls(graph=graph)
    
    def _config(self,thread_id : str):
        return {"configurable":{"thread_id":thread_id}}
    
    def _build_response(self, result:dict, thread_id:str):
        interruptions = result.get("__interrupt__") 
        
        if interruptions :
            interruption = interruptions[0]
            return AgentResponse(thread_id=thread_id,status="review_required",review= interruption.value)

        return AgentResponse(thread_id=thread_id, status="completed", answer=result["messages"][-1].text)
    
    async def send_message(self, request: ChatRequest):
        thread_id = request.thread_id or str(uuid4())
        result = await self.graph.ainvoke(
            {
                "messages": [
                    HumanMessage(
                        content=request.message,
                    )
                ],
                "review_response": None,
            },
            config=self._config(thread_id),
        )

        return self._build_response(
            result=result,
            thread_id=thread_id,
        )
        
    async def send_review(self, thread_id ,request:ReviewRequest):
            result = await self.graph.ainvoke(
            Command(
                resume={
                    "decision": request.decision,
                }
            ),
            config=self._config(thread_id),
            )
            
            return self._build_response(result=result , thread_id=thread_id)
