# Create server parameters for stdio connection
from agents.tools.tools import client
from utils.cutomLogger import customLogger
from settings import llm, pl_prompt

from langgraph.prebuilt import create_react_agent
from langchain.schema import HumanMessage, SystemMessage, Document, AIMessage

from langgraph.checkpoint.memory import MemorySaver

import re

from typing import TypedDict, List

_LOGGER = customLogger.getLogger(__name__)
POSTFIX = "\n\nИсправь, пожалуйста, и сгенерируй описание заново."

class PlAgentState(TypedDict):
    task: str
    result: str
    messages: List

class PlAgent:
    def __init__(self, tools):
        llm_with_functions = llm.bind_functions(tools)
        self.agent = create_react_agent(llm_with_functions, tools, checkpointer=MemorySaver())

    @classmethod
    async def create(cls):
        tools = await client.get_tools(server_name="planer")
        return cls(tools)


    async def run_qa_agent(self, state:PlAgentState, config:dict):
        _LOGGER.info(f"Status: planner_agent, thread_id: {config['configurable']['thread_id']}")
        # state["questions"] = ""
        if "messages" in state and state["messages"]:
            old_messages = state["messages"]
            request = state["messages"][-1].content + POSTFIX

        else:
            old_messages = []
            request = pl_prompt.format(system_requirements=state["task"])
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