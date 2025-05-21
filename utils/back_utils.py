import settings
from .cutomLogger import customLogger
from .utils import create_agents, run_agent, postprocess_response, update_progress_html, router, wrapp_header
import gradio as gr

_LOGGER = customLogger.getLogger(__name__)
AGENTS = create_agents()


def action_push_submit_button(user_input, state):
    curent_status = state["status"]
    current_agent = AGENTS[curent_status]
    current_state = state["agent_states"][curent_status]
    current_config = state["configs"][curent_status]

    _LOGGER.info(f"CURRENT_AGENT: {curent_status}")
    user_msg = {"role": "user", "content": user_input}
    state["messages"].append(user_msg)

    yield (
        gr.update(value=state["messages"]),
        gr.update(value=state),
        gr.update(value=state["md_value"]),
        gr.update(value=state["files_visible"], visible=state["file_visible_status"]),
        ""
    )

    response = run_agent(current_agent, user_input, current_state, current_config)
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

def action_click_next_button(state):
    bar_html, state["progress"] = update_progress_html(state["progress"])
    try:
        state = router(state)
        curent_status = state['status']
        user_msg = {"role": "user", "content": settings.NEXT_TASK[curent_status]}
        state["messages"].append(user_msg)
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
        current_agent = AGENTS[curent_status]
        current_state = state["agent_states"][curent_status]
        current_config = state["configs"][curent_status]
        user_input = ""
        response = run_agent(current_agent, user_input, current_state, current_config)
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