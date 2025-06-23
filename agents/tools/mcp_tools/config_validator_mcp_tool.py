import json
import logging
import re
import sys
from json.decoder import JSONDecodeError
from typing import List, Optional
from xml.dom import ValidationErr

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, validator


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


class Server(BaseModel):
    serverName: str
    tools: List[Tool]


class Agent(BaseModel):
    agentName: str
    agentDescription: str
    agentType: str
    servers: List[str]

    @validator("agentType")
    def validate_agent_type(cls, v):
        allowed = {"agent_with_tools", "orchestrator"}
        if v not in allowed:
            raise ValueError(f"agentType must be one of {allowed}")
        return v


class SystemSpec(BaseModel):
    projectName: str
    projectDesc: str
    systemType: str
    graph: Graph
    agents: List[Agent]
    servers: List[Server]

    @validator("systemType")
    def validate_system_type(cls, v):
        allowed = {"workflow", "orchestrator"}
        if v not in allowed:
            raise ValueError(f"systemType must be one of {allowed}")
        return v

    class Config:
        extra = "forbid"


def parse_json(s: str):
    match = re.search(r"```json\s*(.*?)\s*```", s, re.DOTALL)
    if match:
        result_str = match.group(1)
        result = json.loads(result_str)
        return result
    else:
        raise JSONDecodeError("Incorrect JSON")


_LOGGER = logging.getLogger(__name__)


mcp = FastMCP("config", port="8001")


@mcp.tool()
def check_config(config_file):
    """
    Use this tool to check the generated config for correctness.
    """
    _LOGGER.info(f" ! check_config tool with config {str(config_file)}")
    result = "CONFIG INVALID. Check format."
    try:
        file = parse_json(config_file)
        spec = SystemSpec(**file)
        result = "CONFIG VALID"
        _LOGGER.info(result)
    except ValidationErr as e:
        result = f"Validation failed: {e}"
        _LOGGER.info(result)
    except JSONDecodeError as e:
        result = f"Incorrect JSON. Check it."
        _LOGGER.info(result)
    except SyntaxError as e:
        result = f"Request failed: config must contain ```json. {e}"
        _LOGGER.info(result)
    except Exception as e:
        result = f"Validation failed: {e}"
        _LOGGER.info(result)
    finally:
        return result

if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    mcp.run(transport=transport)
