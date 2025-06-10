from agents.tools.mcp_tools.tools import client
from utils.cutomLogger import customLogger
from settings import llm, pl_prompt

from langgraph.prebuilt import create_react_agent
from langchain.schema import HumanMessage

from langgraph.checkpoint.memory import MemorySaver

import re
import asyncio
from typing import TypedDict, List

_LOGGER = customLogger.getLogger(__name__)
POSTFIX = "\n\nИсправь, пожалуйста, и сгенерируй план разработки полностью заново."

class PlAgentState(TypedDict):
    task: str
    result: str
    messages: List

class PlAgent:
    def __init__(self):
        pass

    async def create(self):
        tools = await client.get_tools(server_name="planer")
        llm_with_functions = llm.bind_functions(tools)
        self.agent = create_react_agent(llm_with_functions, tools, checkpointer=MemorySaver())

    async def run_qa_agent(self, state:PlAgentState, config:dict):
        _LOGGER.info(f"Status: planner_agent, thread_id: {config['configurable']['thread_id']}")
        # state["questions"] = ""
        if "messages" in state and state["messages"]:
            old_messages = state["messages"]
            request = state["messages"][-1].content + POSTFIX

        else:
            old_messages = []
            request = state["task"]
        _LOGGER.info(f"PL REQUEST: {request}")
        request = {
            "messages": [HumanMessage(content=request)]
        }
        response = await self.agent.ainvoke(request, config=config)
        if isinstance(response, dict):
            result = response["messages"][-1].content
        else:
            result = response
        _LOGGER.info(f"PL RESPONSE: {result}")
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

    def add_message(self, state:PlAgentState, msg:str):
        if "messages" in state and state["messages"]:
            old_messages = state["messages"]
        else:
            old_messages = []
        state["messages"] = old_messages + [HumanMessage(content=msg)]
        return state

    def get_result(self, state:PlAgentState):
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

    async def run(self, msg: str, state:PlAgentState, config:dict):
        if not "messages" in state or not state["messages"]:
            await self.create()
            state["task"] = pl_prompt.format(
                system_requirements=state["task"]
            )
        else:
            state = self.add_message(state, msg)
        state = await self.run_qa_agent(state, config)
        response = self.get_result(state)
        response["state"] = state
        return response
