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
    elif cur_status == "SA":
        next_status = "PL"
        state["agent_states"][next_status]["task"] = state["results"]["SA"]
    elif cur_status == "PL":
        next_status = "CO"
        state["agent_states"][next_status]["task"] = state["results"]["PL"]
    else:
        raise StopIteration
    state["status"] = next_status
    return state