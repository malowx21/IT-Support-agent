from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware


from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from api.schemas import AgentResponse, ChatRequest, ReviewRequest

from api.service import AgentService


# Un gestionnaire de contexte permet de gerer la connexion à et la déco à l'app
@asynccontextmanager
async def lifespan(app:FastAPI):
    async with AsyncSqliteSaver.from_conn_string("data/checkpoints.db") as checkpointer :
        app.state.agent_service = await AgentService.create(checkpointer=checkpointer)
        yield
    
app = FastAPI(title= "Support Agent API ",
              description="API d'un agent de support IT", version="0.1.0",lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/chat")
async def chat(payload: ChatRequest,request: Request):
    service = request.app.state.agent_service
    return await service.send_message(payload)

@app.post("/chat/{thread_id}/review")
async def review(thread_id:str, payload:ReviewRequest,request:Request):
    service = request.app.state.agent_service
    return await service.send_review(thread_id,payload)
