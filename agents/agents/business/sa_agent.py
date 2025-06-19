from settings import llm, sa_prompt, sa_instruction
from utils.cutomLogger import customLogger

from langchain.schema import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, List
from typing_extensions import TypedDict

import re

_LOGGER = customLogger.getLogger(__name__)
POSTFIX = "\n\nИсправь, пожалуйста, и сгенерируй системную аналитику заново."


class SaAgentState(TypedDict):
    task: str
    description: str
    ba_requirements: str
    messages: List
    result: str
    questions: List


class SaAgent:
    def __init__(self):
        self.agent = self.create_qa_agent()

    def create_qa_agent(self):
        agent = create_react_agent(llm, tools=[], checkpointer=MemorySaver())
        return agent

    async def run_qa_agent(self, state: SaAgentState, config: dict):
        _LOGGER.info(
            f"Status: sa_agent_node, thread_id: {config['configurable']['thread_id']}"
        )
        state["questions"] = ""
        if "messages" in state and state["messages"]:
            old_messages = state["messages"]
            request = state["messages"][-1].content + POSTFIX
        else:
            old_messages = []
            request = state["task"]
        request = {"messages": [HumanMessage(content=request)]}
        _LOGGER.info(f"SA REQUEST: {request}")
        response = await self.agent.ainvoke(request, config=config)
        if isinstance(response, dict):
            result = response["messages"][-1].content
        else:
            result = response
        _LOGGER.info(f"SA RESPONSE: {result}")

        matches = re.findall(r"\[ВОПРОС\](.*?)\[/ВОПРОС\]", result, re.DOTALL)
        if matches:
            ques_string = [f"{i + 1}. {s}" for i, s in enumerate(matches)]
            state["questions"] = "Возникли вопросы:\n" + "\n".join(ques_string)
        else:
            state["result"] = result
        state["messages"] = old_messages + [
            HumanMessage(content=result, name="Аналитик")
        ]
        return state

    def add_message(self, state: SaAgentState, msg: str):
        if "messages" in state and state["messages"]:
            old_messages = state["messages"]
        else:
            old_messages = []
        state["messages"] = old_messages + [HumanMessage(content=msg)]
        return state

    def get_result(self, state: SaAgentState):
        if "result" in state and state["result"]:
            return {"status": "OK", "content": state["result"]}
        elif "questions" in state and state["questions"]:
            return {"status": "QUES", "content": state["questions"]}
        else:
            return {"status": "FAIL", "content": "Возникла ошибка"}

    async def run(self, msg: str, state: SaAgentState, config: dict):
        if "messages" not in state or not state["messages"]:
            state["task"] = sa_prompt.format(
                sa_instruction=sa_instruction,
                ba_requirements=state["ba_requirements"],
                description=state["description"],
            )
        else:
            state = self.add_message(state, msg)
        state = await self.run_qa_agent(state, config)
        response = self.get_result(state)
        response["state"] = state
        return response
