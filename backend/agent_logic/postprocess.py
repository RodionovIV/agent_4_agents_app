import settings

import subprocess


def save_content(content, filename):
    with open(filename, "w") as f:
        f.write(content)


def render_mermaid(_input, _output):
    subprocess.run(
        [
            "mmdc",
            "-i",
            _input,
            "-o",
            _output,
            "-t",
            "dark",  # или 'dark', 'forest', 'neutral'
            "-b",
            "black",
            "--puppeteerConfigFile",
            settings.puppeteer_config,
        ],
        check=True,
    )


def postprocess_response(state, response):
    curent_status = state["status"]
    if curent_status == "CO":
        repo_name = state["agent_states"][curent_status]["repo_name"]
        msg = settings.RESPONSE_STATUS[curent_status].format(project_name=repo_name)
        return msg, state
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
