from settings import llm, ba_prompt, ba_instruction
from utils.cutomLogger import customLogger

from langchain.agents import initialize_agent, AgentType, Tool
from langchain.memory import ConversationBufferMemory
from langgraph.graph import StateGraph
from langchain.chat_models import ChatOpenAI
from langchain_gigachat.chat_models import GigaChat
from langchain.schema import HumanMessage, SystemMessage, Document, AIMessage
from langchain.vectorstores import FAISS
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END, MessagesState, START
from typing import TypedDict, Optional, Literal, List, Dict
from typing_extensions import TypedDict

import datetime
import warnings
import os
import re

_LOGGER = customLogger.getLogger(__name__)
POSTFIX = "\n\nИсправь, пожалуйста, и сгенерируй бизнес-требования заново."


class BaAgentState(TypedDict):
    task: str
    messages: List
    result: str
    questions: List

class BaAgent:
    def __init__(self):
        self.ba_agent = self.create_qa_agent()

    def create_qa_agent(self):
        ba_agent = create_react_agent(llm, tools=[], checkpointer=MemorySaver())
        return ba_agent

    def run_qa_agent(self, state:BaAgentState, config:dict):
        _LOGGER.info(f"Status: ba_agent_node, thread_id: {config['configurable']['thread_id']}")
        state["questions"] = ""
        if "messages" in state and state["messages"]:
            old_messages = state["messages"]
            request = state["messages"][-1].content + POSTFIX
            _LOGGER.info(f"BA REQUEST: {request}")
        else:
            old_messages = []
            request = state["task"]
        request = {
            "messages": [HumanMessage(content=request)]
        }
        response = self.ba_agent.invoke(request, config=config)
        if isinstance(response, dict):
            result = response["messages"][-1].content
        else:
            result = response
        _LOGGER.info(f"BA RESPONSE: {result}")
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

    def add_message(self, state:BaAgentState, msg:str):
        if "messages" in state and state["messages"]:
            old_messages = state["messages"]
        else:
            old_messages = []
        state["messages"] = old_messages + [HumanMessage(content=msg)]
        return state

    def get_result(self, state:BaAgentState):
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

    def run(self, msg: str, state:BaAgentState, config:dict):
        if not "messages" in state or not state["messages"]:
            state["task"] = ba_prompt.format(task=state["task"], ba_instruction=ba_instruction)
        else:
            state = self.add_message(state, msg)
        state = self.run_qa_agent(state, config)
        response = self.get_result(state)
        response["state"] = state
        return response





