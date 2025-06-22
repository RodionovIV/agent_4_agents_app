from typing import Dict, List, TypedDict

from langchain.schema import HumanMessage


class TextFormatter:
    @staticmethod
    def format_questions(questions: List[str]) -> str:
        ques_string = "\n".join([f"{i + 1}. {s}" for i, s in enumerate(questions)])
        return ques_string

    @staticmethod
    def question_agent_request(messages: List, postfix: str, state: TypedDict) -> str:
        len_human_messages = len(
            [1 for msg in messages if isinstance(msg, HumanMessage)]
        )
        tmp_msg = state["messages"][-1].content
        if len_human_messages > 2:
            request = tmp_msg + postfix
        else:
            request = f"Ответы на вопросы: {tmp_msg}"
        return request

    @staticmethod
    def agent_request(request: str) -> Dict[str, List]:
        return {"messages": [HumanMessage(content=request)]}

    @staticmethod
    def add_message(state: TypedDict, msg: str):
        if "messages" in state and state["messages"]:
            old_messages = state["messages"]
        else:
            old_messages = []
        state["messages"] = old_messages + [HumanMessage(content=msg)]
        return state
