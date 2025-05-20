from frontend.utils import css_utils
from agents.ba_agent import BaAgent, BaAgentState

import gradio as gr
import random
from datetime import datetime
from uuid import uuid4

LOGO_FILE = "src/devil_2_without.png"
SAVE_PATH = "tmp/test.md"

BA_AGENT = BaAgent()

def save_msg(content):
    with open(SAVE_PATH, "w") as f:
        f.write(content)

def process_msg(msg):
    pass
    #     msgs = [
    #         {"role":"assistant", "content":"BAD"},
    #         {"role":"assistant", "content":"GOOD"}
    #     ]
    # return random.choice(msgs)

gen_messages = process_msg("test")

def run_web_interface():
    with gr.Blocks() as demo:
        state = gr.State({
            "messages": [],
            "md_value": "",
            "file_path": SAVE_PATH,
            "ba_agent": True,
            "ba_agent_state": BaAgentState(),
            "ba_config": {"configurable": {"thread_id": str(uuid4())}}
        })
        with gr.Row():
            logo_image = gr.Image(LOGO_FILE,
                                  label="v0.0",
                                  show_download_button=False,
                                  show_fullscreen_button=False,
                                  show_label=False,
                                  height=100,
                                  width=100,
                                  container=False
                              )
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
                file_ = gr.File(visible=False)

        @submit_button.click(inputs=[user_input, state], outputs=[user_input, chat_ui, state, markdown, file_])
        @user_input.submit(inputs=[user_input, state], outputs=[user_input, chat_ui, state, markdown, file_])
        def action_push_submit_button(user_input, state):
            file_visible = False
            user_msg = {"role":"user", "content":user_input}
            state["messages"].append(user_msg)
            response = BA_AGENT.run(user_input, state["ba_agent_state"], state["ba_config"])
            state["ba_agent_state"] = response["state"]
            if response["status"] != "OK":
                msg = response["content"]
            else:
                msg = "Требования успешно сгенерированы"
                state["md_value"] = response["content"]
                # save_msg(response["content"])
                # file_visible = True
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
                gr.update(value=[SAVE_PATH, SAVE_PATH], visible=file_visible)
            )

    # demo.css = css_utils.css_settings
    return demo

if __name__ == "__main__":
    # app_instance = AppInterface()
    demo = run_web_interface()
    demo.launch(server_name="0.0.0.0", server_port=36432)