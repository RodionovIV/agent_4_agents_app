import settings
from agents.desc_agent import DescAgentState, DescAgent
from agents.graph_agent import GraphAgentState, GraphAgent
from agents.ba_agent import BaAgentState, BaAgent
from agents.sa_agent import SaAgentState, SaAgent

from uuid import uuid4
from datetime import datetime

def save_content(content, filename):

    with open(filename, "w") as f:
        f.write(content)

def wrapp_header(msg):
    return f'<h1 align="center">{msg}</h1>'

def process_msg(msg):
    pass
    #     msgs = [
    #         {"role":"assistant", "content":"BAD"},
    #         {"role":"assistant", "content":"GOOD"}
    #     ]
    # return random.choice(msgs)

def update_progress_html(progress):
    new_progress = min(progress + 25, 100)
    bar_html = f"""
    <div style='width: 100%; background-color: #eee; border-radius: 10px; overflow: hidden; height: 30px;'>
        <div style='width: {new_progress}%; background-color: #4CAF50; height: 100%; text-align: center; color: white; line-height: 30px;'>
            {new_progress}%
        </div>
    </div>
    """
    return bar_html, new_progress

def make_config():
    return {
        "configurable":
            {
                "thread_id": str(uuid4())
            }
    }

def setup_initial_state():
    state = {
        "messages": [],
        "md_value": " ",
        "file_path": settings.SAVE_PATH,
        "agent_states": {
            "DESC": DescAgentState(),
            "GRAPH": GraphAgentState(),
            "BA": BaAgentState(),
            "SA": SaAgentState()
        },
        "configs": {
            "DESC": make_config(),
            "GRAPH": make_config(),
            "BA": make_config(),
            "SA": make_config()
        },
        "files": {
            "DESC": create_filename("description"),
            "GRAPH": create_filename("graph"),
            "BA": create_filename("business_requirements"),
            "SA": create_filename("system_requirements")
        },
        "files_visible": [],
        "results": dict(),
        "status": "DESC",
        "status_iterator": iter(settings.NEXT_STATUS_LIST),
        "progress": 0
    }
    return state

def create_agents():
    return {
        "DESC": DescAgent(),
        "GRAPH": GraphAgent(),
        "BA": BaAgent(),
        "SA": SaAgent()
    }

def create_filename(prefix):
    datetime_str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    return f"{settings.base_dir}/{prefix}_{datetime_str}.md"

def router(state):
    cur_status = state["status"]
    if cur_status == "DESC":
        next_status = "GRAPH"
        state["agent_states"][next_status]["task"] = state["agent_states"][cur_status]["task"]
        state["agent_states"][next_status]["description"] = state["results"][cur_status]
    elif cur_status == "GRAPH":
        next_status = "BA"
        state["agent_states"][next_status]["task"] = state["agent_states"][cur_status]["description"]
    elif cur_status == "BA":
        next_status = "SA"
        state["agent_states"][next_status]["description"] = state["results"]["DESC"]
        state["agent_states"][next_status]["ba_requirements"] = state["results"]["BA"]
    else:
        raise StopIteration
    state["status"] = next_status
    return state

