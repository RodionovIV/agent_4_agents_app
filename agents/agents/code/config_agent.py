from langchain.schema import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from abstract.abstract_agent import AbstractAgent
from agents.agents.states.code_state import CoAgentState
from agents.tools.mcp_tools.tools import client
from agents.utils.text_formatter import TextFormatter
from settings import llm
from utils.cutomLogger import customLogger

_LOGGER = customLogger.getLogger(__name__)

POSTFIX = "\n\nИсправь, пожалуйста, и сгенерируй код полностью заново."


class ConfigAgent(AbstractAgent):
    def __init__(self):
        pass

    async def create(self):
        config_tools = await client.get_tools(server_name="config")
        self.agent = create_react_agent(llm, config_tools, checkpointer=MemorySaver())

    async def run_agent(self, state: CoAgentState, config: dict):
        class_name = self.__class__.__name__.lower()
        _LOGGER.info(
            f"Status: {class_name}, thread_id: {config['configurable']['thread_id']}"
        )

        if "messages" in state and state["messages"]:
            old_messages = state["messages"]
            request = state["messages"][-1].content + POSTFIX

        else:
            old_messages = []
            request = state["config_task"]

        _LOGGER.info(f"{class_name}_request: {request}")
        request = TextFormatter.agent_request(request)
        response = await self.agent.ainvoke(request, config=config)

        if isinstance(response, dict):
            result = response["messages"][-1].content
        else:
            result = response

        _LOGGER.info(f"{class_name}_response: {result}")

        state["config_result"] = result
        state["messages"] = old_messages + [
            HumanMessage(content=result, name="Аналитик")
        ]
        return state
