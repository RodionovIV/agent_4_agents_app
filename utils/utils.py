import settings
from agents.desc_agent import DescAgentState, DescAgent
from agents.graph_agent import GraphAgentState, GraphAgent
from agents.ba_agent import BaAgentState, BaAgent
from agents.sa_agent import SaAgentState, SaAgent

from uuid import uuid4
from datetime import datetime
import subprocess

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
        "init": False,
        "messages": [],
        "md_value": " ",
        "agent_states": {
            "DESC": DescAgentState(),
            "GRAPH": GraphAgentState(),
            "BA": BaAgentState(),
            "SA": SaAgentState()
        },
        "configs": {
            "DESC": "EMPTY",
            "GRAPH": "EMPTY",
            "BA": "EMPTY",
            "SA": "EMPTY"
        },
        "files": {
            "DESC": "EMPTY",
            "GRAPH": "EMPTY",
            "BA": "EMPTY",
            "SA": "EMPTY"
        },
        "mmd": create_filename("mermaid"),
        "mmd_picture": create_filename("picture"),
        "file_visible_status": False,
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
    if prefix == "mermaid":
        return f"{settings.save_dir}/{prefix}_{datetime_str}.mmd"
    elif prefix == "picture":
        return f"{settings.save_dir}/{prefix}_{datetime_str}.png"
    return f"{settings.save_dir}/{prefix}_{datetime_str}.md"

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

def run_agent(current_agent, user_input, current_state, current_config):
    response = current_agent.run(user_input, current_state, current_config)
    return response

def postprocess_response(state, response):
    curent_status = state["status"]
    state["agent_states"][curent_status] = response["state"]
    if response["status"] != "OK":
        msg = response["content"]
    else:
        msg = settings.RESPONSE_STATUS[curent_status]
        state["results"][curent_status] = response["content"]
        state["md_value"] = response["content"] + settings.WATEMARK
        state["file_visible_status"] = True
        save_content(response["content"], state["files"][curent_status])
        if state["files"][curent_status] not in state["files_visible"]:
            state["files_visible"].append(state["files"][curent_status])
        if "mermaid" in response and response["mermaid"]:
            save_content(response["mermaid"], state["mmd"])
            try:
                render_mermaid(state["mmd"], state["mmd_picture"])
                if state["mmd_picture"] not in state["files_visible"]:
                    state["files_visible"].append(state["mmd_picture"])
            except:
                pass
    return msg, state

def render_mermaid(_input, _output):
    subprocess.run([
        "mmdc",
        "-i", _input,
        "-o", _output,
        "-t", "dark", # или 'dark', 'forest', 'neutral'
        "-b", "black",
        "--puppeteerConfigFile", settings.puppeteer_config
    ], check=True)