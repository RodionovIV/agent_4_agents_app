from agents.tools.mcp_tools.tools import client
from utils.cutomLogger import customLogger
from settings import llm, coder_prompt, git_prompt

from langgraph.prebuilt import create_react_agent
from langchain.schema import HumanMessage

from langgraph.checkpoint.memory import MemorySaver

import re
from uuid import uuid4
import asyncio
from typing import TypedDict, List
_LOGGER = customLogger.getLogger(__name__)

POSTFIX = "\n\nИсправь, пожалуйста, и сгенерируй код полностью заново."

class CoAgentState(TypedDict):
    task: str
    repo_name: str

class CoAgent:
    def __init__(self):
        pass

    async def create(self):
        coder_tools = await client.get_tools(server_name="coder")
        git_tools = await client.get_tools(server_name="git")

        llm_with_functions = llm.bind_functions(coder_tools)
        self.coder_agent = create_react_agent(llm, coder_tools, checkpointer=MemorySaver())

        llm_with_functions = llm.bind_functions(git_tools)
        self.git_agent = create_react_agent(llm, git_tools, checkpointer=MemorySaver())

    async def run_qa_agent(self, state:CoAgentState, config:dict):
        _LOGGER.info(f"Status: coder_agent, thread_id: {config['configurable']['thread_id']}")
        # state["questions"] = ""
        if "messages" in state and state["messages"]:
            old_messages = state["messages"]
            request = state["messages"][-1].content + POSTFIX

        else:
            old_messages = []
            request = state["task"]
        _LOGGER.info(f"CODER REQUEST: {request}")
        request = {
            "messages": [HumanMessage(content=request)]
        }
        response = await self.coder_agent.ainvoke(request, config=config)
        git_config = {
            "configurable": {
                "thread_id": str(uuid4())
            },
            "recursion_limit": 100
        }
        git_message = {
            "messages": [HumanMessage(
                content=git_prompt.format(project_name=state["repo_name"]))
            ]
        }
        if isinstance(response, dict):
            result = response["messages"][-1].content
        else:
            result = response
        _LOGGER.info(f"CODER RESPONSE: {result}")

        response = await self.git_agent.ainvoke(git_message, config=git_config)
        if isinstance(response, dict):
            result = response["messages"][-1].content
        else:
            result = response
        _LOGGER.info(f"GIT RESPONSE: {result}")

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

    def add_message(self, state:CoAgentState, msg:str):
        if "messages" in state and state["messages"]:
            old_messages = state["messages"]
        else:
            old_messages = []
        state["messages"] = old_messages + [HumanMessage(content=msg)]
        return state

    def get_result(self, state:CoAgentState):
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

    async def run(self, msg: str, state:CoAgentState, config:dict):
        if not "messages" in state or not state["messages"]:
            await self.create()
            state["task"] = coder_prompt.format(
                plan=state["task"],
                project_name=state["repo_name"]
            )
        else:
            state = self.add_message(state, msg)
        state = await self.run_qa_agent(state, config)
        # response = self.get_result(state)
        # response["state"] = state
        return {"status": "OK"}