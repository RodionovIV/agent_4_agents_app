from settings import llm, describer_prompt, instruments
from utils.cutomLogger import customLogger
from langchain.schema import HumanMessage, SystemMessage, Document, AIMessage

from langchain.chains import RetrievalQA

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Optional, Literal, List, Dict
from typing_extensions import TypedDict

import datetime
import warnings
import os
import re

_LOGGER = customLogger.getLogger(__name__)
POSTFIX = "\n\nИсправь, пожалуйста, и сгенерируй описание заново."


class DescAgentState(TypedDict):
    task: str
    messages: List
    questions: str
    result: str

class DescAgent:
    def __init__(self):
        self.desc_agent = self.create_qa_agent()

    def create_qa_agent(self):
        desc_agent = create_react_agent(llm, tools=[], checkpointer=MemorySaver())
        return desc_agent

    def run_qa_agent(self, state:DescAgentState, config:dict):
        _LOGGER.info("Status: desc_agent_node")
        state["questions"] = ""
        if "messages" in state and state["messages"]:
            old_messages = state["messages"]
            request = state["messages"][-1].content + POSTFIX
            _LOGGER.info(f"REQUEST: {request}")

        else:
            old_messages = []
            request = state["task"]
        request = {
            "messages": [HumanMessage(content=request)]
        }
        response = self.desc_agent.invoke(request, config=config)
        if isinstance(response, dict):
            result = response["messages"][-1].content
        else:
            result = response
        _LOGGER.info(f"DESC RESPONSE: {result}")
        matches = re.findall(r'\[ВОПРОС\](.*?)\[/ВОПРОС\]', result, re.DOTALL)
        if matches:
            ques_string = [
                f"{i+1}. {s}"
                for i, s in enumerate(matches)
            ]
            state["questions"] = "Возникли вопросы:\n" + "\n".join(ques_string)
        else:
            state["result"] = result
        state["messages"] =  old_messages + [HumanMessage(content=result, name="Аналитик")]
        return state

    def add_message(self, state:DescAgentState, msg:str):
        if "messages" in state and state["messages"]:
            old_messages = state["messages"]
        else:
            old_messages = []
        state["messages"] = old_messages + [HumanMessage(content=msg)]
        return state

    def get_result(self, state:DescAgentState):
        if "result" in state and state["result"]:
            return {
                "status": "OK",
                "content": state["result"]
            }
        elif "questions" in state and state["questions"]:
            return {
                "status": "QUES",
                "content": state["questions"]
            }
        else:
            return {
                "status":"FAIL",
                "content": "Возникла ошибка"
            }

    def run(self, msg: str, state:DescAgentState, config:dict):
        if not "messages" in state or not state["messages"]:
            state["task"] = describer_prompt.format(task=msg, instruments=instruments)
        else:
            state = self.add_message(state, msg)
        state = self.run_qa_agent(state, config)
        response = self.get_result(state)
        response["state"] = state
        return response





