from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from abstract.abstract_agent import AbstractAgent
from agents.utils.parser import Parser
from agents.utils.text_formatter import TextFormatter
from settings import llm
from utils.cutomLogger import customLogger
from uuid import uuid4
from typing import Dict

_LOGGER = customLogger.getLogger(__name__)


class PromptAgent(AbstractAgent):
    def __init__(self):
        self.agent = self.create_agent()

    def create_agent(self):
        agent = create_react_agent(llm, tools=[], checkpointer=MemorySaver())
        return agent

    @staticmethod
    def __create_config():
        return {
            "configurable": {"thread_id": str(uuid4())},
            "recursion_limit": 100,
        }

    async def run_agent(self, task: str):
        class_name = self.__class__.__name__.lower()
        config = PromptAgent.__create_config()
        _LOGGER.info(
            f"Status: {class_name}, thread_id: {config['configurable']['thread_id']}"
        )

        request = task

        _LOGGER.info(f"{class_name}_request: {request}")

        request = TextFormatter.agent_request(request)

        response = await self.agent.ainvoke(request, config=config)
        if isinstance(response, dict):
            result = response["messages"][-1].content
        else:
            result = response
        _LOGGER.info(f"{class_name}_response: {result}")

        matches = Parser.parse_json(result)
        prompt = ""
        if matches:
            prompt = matches["prompt"]
        return prompt

    async def run(self, agents_dict: Dict[str, Dict]) -> Dict[str, Dict]:
        for agent in agents_dict:
            agents_dict[agent]["result"] = await self.run_agent(
                agents_dict[agent]["task"]
            )
        return agents_dict
