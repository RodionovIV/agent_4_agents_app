from fastapi import APIRouter
from models.agent import AgentRequest, AgentResponse
from services.agents.graph import create_graph

router = APIRouter()

@router.post("/run_agent", response_model=AgentResponse)
async def process_agent_request(request: AgentRequest):
    graph = await create_graph()
    result = await graph.ainvoke(request.query)
    return AgentResponse(result=result)