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
        state["agent_states"][next_status]["task"] = state["agent_states"][cur_status]["task"]
        state["agent_states"][next_status]["description"] = state["results"][cur_status]
        generate = True
    state["gen_precondition"] = generate
    return state

def save_graph_state(state):
    cur_status = "GRAPH"
    next_status = "BA"
    generate = False
    if state["gen_precondition"]:
        state["agent_states"][next_status]["task"] = state["agent_states"][cur_status]["description"]
        generate = True
    state["gen_precondition"] = generate
    return state

def save_ba_state(state):
    cur_status = "BA"
    next_status = "SA"
    generate = False
    if state["gen_precondition"]:
        state["agent_states"][next_status]["description"] = state["agent_states"][cur_status]["task"]
        state["agent_states"][next_status]["ba_requirements"] = state["results"]["BA"]
        generate = True
    state["gen_precondition"] = generate
    return state

def save_sa_state(state):
    cur_status = "SA"
    next_status = "PL"
    generate = False
    if state["gen_precondition"]:
        state["agent_states"][next_status]["task"] = state["results"]["SA"]
        generate = True
    state["gen_precondition"] = generate
    return state

def save_pl_state(state):
    next_status = "CO"
    generate = False
    if state["gen_precondition"]:
        state["agent_states"][next_status]["task"] = state["results"]["PL"]
    generate = True
    state["gen_precondition"] = generate
    return state

def router(state):
    cur_status = state["status"]
    if cur_status == "DESC":
        next_status = "GRAPH"
        state = save_desc_state(state)
    elif cur_status == "GRAPH":
        next_status = "BA"
        state = save_graph_state(state)
    elif cur_status == "BA":
        next_status = "SA"
        state = save_ba_state(state)
    elif cur_status == "SA":
        next_status = "PL"
        state = save_sa_state(state)
    elif cur_status == "PL":
        next_status = "CO"
        state = save_pl_state(state)
    else:
        raise StopIteration
    state["status"] = next_status
    return state

def check_state(cur_status, user_input, current_state):
    if cur_status == "GRAPH":
        if not "description" in current_state or not current_state["description"]:
            current_state["description"] = user_input
        if not "task" in current_state or not current_state["task"]:
            current_state["task"] = user_input
    elif cur_status == "BA":
        if not "task" in current_state or not current_state["task"]:
            current_state["task"] = user_input
    elif cur_status == "SA":
        if not "ba_requirements" in current_state or not current_state["ba_requirements"]:
            current_state["ba_requirements"] = user_input
        if not "description" in current_state or not current_state["description"]:
            current_state["description"] = user_input
    elif cur_status == "PL":
        if not "task" in current_state or not current_state["task"]:
            current_state["task"] = user_input
    elif cur_status == "CO":
        if not "task" in current_state or not current_state["task"]:
            current_state["task"] = user_input
    return current_state


