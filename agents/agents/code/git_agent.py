from uuid import uuid4

from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from abstract.abstract_agent import AbstractAgent
from agents.agents.states import CoAgentState
from agents.tools.mcp_tools.tools import client
from agents.utils.text_formatter import TextFormatter
from settings import llm
from utils.cutomLogger import customLogger

_LOGGER = customLogger.getLogger(__name__)


class GitAgent(AbstractAgent):
    def __init__(self):
        pass

    async def create(self):
        git_tools = await client.get_tools(server_name="git")
        self.agent = create_react_agent(llm, git_tools, checkpointer=MemorySaver())

    @staticmethod
    def __create_config():
        return {
            "configurable": {"thread_id": str(uuid4())},
            "recursion_limit": 100,
        }

    async def run_agent(self, state: CoAgentState):
        class_name = self.__class__.__name__.lower()
        _LOGGER.info(f"Status: {class_name}")
        config = GitAgent.__create_config()
        request = state["git_task"]
        request = TextFormatter.agent_request(request)

        response = await self.agent.ainvoke(request, config=config)
        if isinstance(response, dict):
            result = response["messages"][-1].content
        else:
            result = response
        _LOGGER.info(f"{class_name}_response: {result}")
        state["git_result"] = result
        return state
