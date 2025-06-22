import settings
from agents.agents.business.desc_agent import DescAgentState, DescAgent
from agents.agents.business.graph_agent import GraphAgentState, GraphAgent
from agents.agents.business.ba_agent import BaAgentState, BaAgent
from agents.agents.business.sa_agent import SaAgentState, SaAgent
from agents.agents.code.planer_agent import PlAgentState, PlAgent
from agents.agents.code.coder_agent import CoAgentState, CoAgent

from datetime import datetime
from uuid import uuid4


def make_config():
    return {"configurable": {"thread_id": str(uuid4())}, "recursion_limit": 100}


def create_agents():
    return {
        "DESC": DescAgent(),
        "GRAPH": GraphAgent(),
        "BA": BaAgent(),
        "SA": SaAgent(),
        "PL": PlAgent(),
        "CO": CoAgent(),
    }


def create_filename(prefix):
    datetime_str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    if prefix == "mermaid":
        return f"{settings.save_dir}/{prefix}_{datetime_str}.mmd"
    elif prefix == "picture":
        return f"{settings.save_dir}/{prefix}_{datetime_str}.png"
    return f"{settings.save_dir}/{prefix}_{datetime_str}.md"


def setup_initial_state():
    state = {
        "init": False,
        "messages": [],
        "md_value": " ",
        "agent_states": {
            "DESC": DescAgentState(),
            "GRAPH": GraphAgentState(),
            "BA": BaAgentState(),
            "SA": SaAgentState(),
            "PL": PlAgentState(),
            "CO": CoAgentState(),
        },
        "configs": {
            "DESC": "EMPTY",
            "GRAPH": "EMPTY",
            "BA": "EMPTY",
            "SA": "EMPTY",
            "PL": "EMPTY",
            "CO": "EMPTY",
            "GIT": "EMPTY",
        },
        "files": {
            "DESC": "EMPTY",
            "GRAPH": "EMPTY",
            "BA": "EMPTY",
            "SA": "EMPTY",
            "PL": "EMPTY",
        },
        "mmd": "EMPTY",
        "mmd_picture": "EMPTY",
        "file_visible_status": False,
        "files_visible": [],
        "results": dict(),
        "status": "DESC",
        "status_iterator": iter(settings.NEXT_STATUS_LIST),
        "progress": 0,
        "repo_name": "EMPTY",
        "gen_precondition": False,
    }
    return state
