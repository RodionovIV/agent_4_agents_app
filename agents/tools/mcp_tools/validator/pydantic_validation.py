import re
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class Node(BaseModel):
    name: str
    to: str


class Graph(BaseModel):
    initialState: str
    nodes: List[Node]


class Tool(BaseModel):
    toolName: str
    toolType: str
    toolDescription: str
    params: Optional[List[str]] = Field(default_factory=list)

    @field_validator("toolType")
    def validate_tool_type(cls, v):
        allowed = {"get_mcp_template", "post_mcp_template"}
        if v not in allowed:
            raise ValueError(f"toolType must be one of {allowed}")
        return v


class Server(BaseModel):
    serverName: str
    tools: List[Tool]


class Agent(BaseModel):
    agentName: str
    agentDescription: str
    agentType: str
    servers: List[str]

    @field_validator("agentType")
    def validate_agent_type(cls, v):
        allowed = {"agent_with_tools", "orchestrator"}
        if v not in allowed:
            raise ValueError(f"agentType must be one of {allowed}")
        return v

    @field_validator("agentName")
    def validate_agent_name(cls, v):
        if not re.fullmatch(r'[A-Za-z]+', v):
            raise ValueError("agentName must contain only English letters (A-Z, a-z)")
        return v



class SystemSpec(BaseModel):
    projectName: str
    projectDesc: str
    systemType: str
    graph: Graph
    agents: List[Agent]
    servers: List[Server]

    @field_validator("systemType")
    def validate_system_type(cls, v):
        allowed = {"workflow", "orchestrator"}
        if v not in allowed:
            raise ValueError(f"systemType must be one of {allowed}")
        return v

    class Config:
        extra = "forbid"
