from settings import STATUS_LIST


def wrapp_header(msg):
    return f'<h1 align="center">{msg}</h1>'


def update_progress_html(progress):
    new_progress = min(progress + 17, 100)
    bar_html = f"""
    <div style='width: 100%; background-color: #eee; border-radius: 10px; overflow: hidden; height: 30px;'>
        <div style='width: {new_progress}%; background-color: #4CAF50; height: 100%; text-align: center; color: white; line-height: 30px;'>
            {new_progress}%
        </div>
    </div>
    """
    return bar_html, new_progress


def save_desc_state(state):
    cur_status = "DESC"
    next_status = "GRAPH"
    generate = False
    if state["gen_precondition"]:
        desc = state["results"]["DESC"]
        task = state["agent_states"]["DESC"]["task"]
        state["agent_states"]["BA"]["task"] = desc
        state["agent_states"]["GRAPH"]["task"] = task
        state["agent_states"]["GRAPH"]["description"] = desc
        state["agent_states"]["CO"]["desc"] = desc
        generate = True
    state["gen_precondition"] = generate
    return state


def save_graph_state(state):
    cur_status = "GRAPH"
    next_status = "BA"
    generate = False
    if state["gen_precondition"]:
        graph = state["agent_states"]["GRAPH"]["result"]
        state["agent_states"]["CO"]["task"] = graph
        generate = True
    state["gen_precondition"] = generate
    return state


def save_ba_state(state):
    cur_status = "BA"
    next_status = "SA"
    generate = False
    if state["gen_precondition"]:
        state["agent_states"]["SA"]["description"] = state["agent_states"]["BA"]["task"]
        state["agent_states"]["SA"]["ba_requirements"] = state["results"]["BA"]
        generate = True
    state["gen_precondition"] = generate
    return state


def save_sa_state(state):
    cur_status = "SA"
    next_status = "PL"
    generate = False
    if state["gen_precondition"]:
        state["agent_states"]["PL"]["task"] = state["results"]["SA"]
        generate = True
    state["gen_precondition"] = generate
    return state


def save_pl_state(state):
    next_status = "CO"
    generate = False
    if state["gen_precondition"]:
        # state["agent_states"][next_status]["task"] = state["results"]["PL"]
        generate = True
    state["gen_precondition"] = generate
    return state


def router(state):
    cur_status = state["status"]
    next_status_idx = STATUS_LIST.index(cur_status) + 1
    if next_status_idx < len(STATUS_LIST):
        next_status = STATUS_LIST[next_status_idx]
    if cur_status == "DESC":
        state = save_desc_state(state)
    elif cur_status == "GRAPH":
        state = save_graph_state(state)
    elif cur_status == "BA":
        state = save_ba_state(state)
    elif cur_status == "SA":
        state = save_sa_state(state)
    elif cur_status == "PL":
        state = save_pl_state(state)
    else:
        raise StopIteration
    state["status"] = next_status
    return state


def check_state(cur_status, user_input, current_state):
    if cur_status == "GRAPH":
        if "description" not in current_state or not current_state["description"]:
            current_state["description"] = user_input
        if "task" not in current_state or not current_state["task"]:
            current_state["task"] = user_input
    elif cur_status == "BA":
        if "task" not in current_state or not current_state["task"]:
            current_state["task"] = user_input
    elif cur_status == "SA":
        if (
            "ba_requirements" not in current_state
            or not current_state["ba_requirements"]
        ):
            current_state["ba_requirements"] = user_input
        if "description" not in current_state or not current_state["description"]:
            current_state["description"] = user_input
    elif cur_status == "PL":
        if "task" not in current_state or not current_state["task"]:
            current_state["task"] = user_input
    elif cur_status == "CO":
        if "repo_name" not in current_state or not current_state["repo_name"]:
            current_state["repo_name"] = user_input
        elif "task" not in current_state or not current_state["task"]:
            current_state["task"] = user_input
            current_state["desc"] = user_input
    return current_state
