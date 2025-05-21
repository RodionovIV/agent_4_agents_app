import settings
from utils.utils import update_progress_html, setup_initial_state
from utils.back_utils import action_push_submit_button, action_click_next_button
from utils.cutomLogger import customLogger

import gradio as gr
_LOGGER = customLogger.getLogger(__name__)
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
                    user_input = gr.Textbox(scale=30, label="", placeholder="Введите текст...", lines=1,)
                    submit_button = gr.Button(scale=1, value="➤")
            with gr.Column():
                markdown = gr.Markdown(label="Результат", max_height=500, value=state.value["md_value"])
        with gr.Row():
            with gr.Column():
                pass
            with gr.Column():
                file_ = gr.File(value=[], visible=False,)

        submit_button.click(inputs=[user_input, state],
                            outputs=[chat_ui, state, markdown, file_, user_input],
                            fn=action_push_submit_button, show_progress_on=[user_input, submit_button])

        user_input.submit(inputs=[user_input, state],
                          outputs=[chat_ui, state, markdown, file_, user_input],
                          fn=action_push_submit_button, show_progress_on=[user_input, submit_button])

        next_button.click(inputs=[state],
                          outputs=[chat_ui, state, markdown, file_, next_button, progress_html, header],
                          fn=action_click_next_button, show_progress_on=[user_input, submit_button])

    return demo

if __name__ == "__main__":
    demo = run_web_interface()
    demo.launch(server_name="0.0.0.0", server_port=36432)