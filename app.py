import time

import settings
from utils.utils import router, wrapp_header, update_progress_html, setup_initial_state, create_agents, save_content
from utils.cutomLogger import customLogger

import gradio as gr
_LOGGER = customLogger.getLogger(__name__)
AGENTS = create_agents()
INIT_BAR, _ = update_progress_html(-25)

def run_web_interface():
    with gr.Blocks() as demo:
        state = gr.State(setup_initial_state())
        with gr.Row():
            logo_image = gr.Image(settings.LOGO_FILE,
                                  show_download_button=False,
                                  show_fullscreen_button=False,
                                  show_label=False,
                                  height=100,
                                  width=100,
                                  container=False
                              )
        with gr.Row():
            header = gr.Markdown(value='<h1 align="center">📝 Генерация описания бизнес-задачи</h1>')
        with gr.Row():
            with gr.Column():
                next_button = gr.Button(scale=1, value=f"Следующий шаг -> 🌐 Граф взаимодействий")
            with gr.Column():
                progress_html = gr.HTML(INIT_BAR)
        with gr.Row():
            with gr.Column():
                chat_ui = gr.Chatbot(type="messages", show_label=False)
                with gr.Row():
                    user_input = gr.Textbox(scale=30, label="", placeholder="Введите текст...", lines=1)
                    submit_button = gr.Button(scale=1, value="➤", elem_id="submit_button")
            with gr.Column():
                markdown = gr.Markdown(label="Результат", max_height=500, value=state.value["md_value"])
        with gr.Row():
            with gr.Column():
                pass
            with gr.Column():
                file_ = gr.File(value=[], visible=False)

        @submit_button.click(inputs=[user_input, state], outputs=[user_input, chat_ui, state, markdown, file_])
        @user_input.submit(inputs=[user_input, state], outputs=[user_input, chat_ui, state, markdown, file_])
        def action_push_submit_button(user_input, state):
            file_visible = False
            curent_status = state["status"]
            current_agent = AGENTS[curent_status]
            current_state = state["agent_states"][curent_status]
            current_config = state["configs"][curent_status]

            _LOGGER.info(f"CURRENT_AGENT: {curent_status}")
            user_msg = {"role":"user", "content":user_input}
            state["messages"].append(user_msg)
            response = current_agent.run(user_input, current_state, current_config)
            state["agent_states"][curent_status] = response["state"]
            if response["status"] != "OK":
                msg = response["content"]
            else:
                msg = settings.RESPONSE_STATUS[curent_status]
                state["results"][curent_status] = response["content"]
                state["md_value"] = response["content"]
                file_visible = True
                save_content(response["content"], state["files"][curent_status])
                state["files_visible"].append(state["files"][curent_status])
            ai_message = {"role": "assistant", "content": msg}
            state["messages"].append(ai_message)

            # if agent_msg == {"role":"assistant", "content":"GOOD"}:
            #     state["md_value"] = "NONO\n" * 500
            #     #save_msg(state["messages"])
            #     file_visible = True

            return (
                "",
                gr.update(value=state["messages"]),
                gr.update(value=state),
                gr.update(value=state["md_value"]),
                gr.update(value=state["files_visible"], visible=file_visible)
            )

        @next_button.click(inputs=[state], outputs=[state, next_button, progress_html, header])
        def click_next_button(state):
            bar_html, state["progress"] = update_progress_html(state["progress"])
            try:
                state = router(state)
                status = state['status']
                button_params = {
                    "value": f"{settings.BUTTON_STATUS[status]}"
                }
                header_params = {
                    "value": wrapp_header(settings.HEADER_STATUS[status]),
                    "visible": True
                }
            except StopIteration:
                header_params = {"visible": False}
                button_params = {"value": "🏁 Конец 🏁"}
            finally:
                return (
                    gr.update(value=state),
                    gr.update(**button_params),
                    gr.update(value=bar_html),
                    gr.update(**header_params)
                )



    # demo.css = css_utils.css_settings
    return demo

if __name__ == "__main__":
    # app_instance = AppInterface()
    demo = run_web_interface()
    demo.launch(server_name="0.0.0.0", server_port=36432)