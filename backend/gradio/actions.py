import settings
from backend.agent_logic.init import create_agents, create_filename, make_config
from backend.agent_logic.in_progress import update_progress_html, router, wrapp_header
from backend.agent_logic.postprocess import postprocess_response
from utils.cutomLogger import customLogger
import gradio as gr

_LOGGER = customLogger.getLogger(__name__)
AGENTS = create_agents()


async def run_agent(current_agent, user_input, current_state, current_config):
    response = await current_agent.run(user_input, current_state, current_config)
    return response

async def action_push_submit_button(user_input, state):
    if not state["init"]:
        _LOGGER.info("Initialize initial state")
        state["init"] = True
        state["configs"]["DESC"] = make_config()
        state["configs"]["GRAPH"] = make_config()
        state["configs"]["BA"] = make_config()
        state["configs"]["SA"] = make_config()
        state["configs"]["PL"] = make_config()
        state["configs"]["CO"] = make_config()
        state["configs"]["GIT"] = make_config()

        state["files"]["DESC"] = create_filename("description")
        state["files"]["GRAPH"] = create_filename("graph")
        state["files"]["BA"] = create_filename("ba_requirements")
        state["files"]["SA"] = create_filename("sa_requirements")
        state["files"]["PL"] = create_filename("dev_plan")

        state["mmd"] = create_filename("mermaid")
        state["mmd_picture"] = create_filename("picture")

        print(state["configs"]["DESC"])


    curent_status = state["status"]
    current_agent = AGENTS[curent_status]
    current_state = state["agent_states"][curent_status]
    current_config = state["configs"][curent_status]

    _LOGGER.info(f"CURRENT_AGENT: {curent_status}")
    user_msg = {"role": "user", "content": user_input}
    state["messages"].append(user_msg)
    if curent_status == "CO":
        state["repo_name"] = user_input

    yield (
        gr.update(value=state["messages"]),
        gr.update(value=state),
        gr.update(value=state["md_value"]),
        gr.update(value=state["files_visible"], visible=state["file_visible_status"]),
        ""
    )

    response = await run_agent(current_agent, user_input, current_state, current_config)
    msg, state = postprocess_response(state, response)
    ai_message = {"role": "assistant", "content": msg}
    state["messages"].append(ai_message)

    yield (
        gr.update(value=state["messages"]),
        gr.update(value=state),
        gr.update(value=state["md_value"]),
        gr.update(value=state["files_visible"], visible=state["file_visible_status"]),
        ""
    )

async def action_click_next_button(state):
    bar_html, state["progress"] = update_progress_html(state["progress"])
    try:
        state = router(state)

        curent_status = state['status']
        user_msg = {"role": "user", "content": settings.NEXT_TASK[curent_status]}
        state["messages"].append(user_msg)
        if curent_status == "CO":
            ai_message = {"role": "assistant", "content": "Введите название репозитория"}
            state["messages"].append(ai_message)
        button_params = {
            "value": f"{settings.BUTTON_STATUS[curent_status]}"
        }
        header_params = {
            "value": wrapp_header(settings.HEADER_STATUS[curent_status]),
            "visible": True
        }
        yield (
            gr.update(value=state["messages"]),
            gr.update(value=state),
            gr.update(value=state["md_value"]),
            gr.update(value=state["files_visible"], visible=state["file_visible_status"]),
            gr.update(**button_params),
            gr.update(value=bar_html),
            gr.update(**header_params),
        )
        if curent_status in {"GRAPH", "BA", "SA", "PL"}:
            current_agent = AGENTS[curent_status]
            current_state = state["agent_states"][curent_status]
            current_config = state["configs"][curent_status]
            user_input = ""
            response = await run_agent(current_agent, user_input, current_state, current_config)
            msg, state = postprocess_response(state, response)
            ai_message = {"role": "assistant", "content": msg}
            state["messages"].append(ai_message)

        yield (
            gr.update(value=state["messages"]),
            gr.update(value=state),
            gr.update(value=state["md_value"]),
            gr.update(value=state["files_visible"], visible=state["file_visible_status"]),
            gr.update(),
            gr.update(),
            gr.update(),
        )

    except StopIteration:
        header_params = {"visible": False}
        button_params = {"value": "🏁 Конец 🏁"}
        yield (
            gr.update(value=state["messages"]),
            gr.update(value=state),
            gr.update(value=state["md_value"]),
            gr.update(value=state["files_visible"], visible=state["file_visible_status"]),
            gr.update(**button_params),
            gr.update(value=bar_html),
            gr.update(**header_params),
        )