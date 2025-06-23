from langchain.schema import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from abstract.abstract_agent import AbstractAgent
from agents.agents.states import PlAgentState
from agents.tools.mcp_tools.tools import client
from agents.utils.result_formatter import ResultFormatter
from agents.utils.text_formatter import TextFormatter
from settings import llm, pl_prompt
from utils.cutomLogger import customLogger

_LOGGER = customLogger.getLogger(__name__)
POSTFIX = "\n\nИсправь, пожалуйста, и сгенерируй план разработки полностью заново."


class PlAgent(AbstractAgent):
    def __init__(self):
        pass

    async def create_agent(self):
        tools = await client.get_tools(server_name="planer")
        llm_with_functions = llm.bind_functions(tools)
        self.agent = create_react_agent(
            llm_with_functions, tools, checkpointer=MemorySaver()
        )

    async def run_agent(self, state: PlAgentState, config: dict):
        class_name = self.__class__.__name__.lower()
        _LOGGER.info(
            f"Status: {class_name}, thread_id: {config['configurable']['thread_id']}"
        )

        if "messages" in state and state["messages"]:
            old_messages = state["messages"]
            request = state["messages"][-1].content + POSTFIX

        else:
            old_messages = []
            request = state["task"]

        _LOGGER.info(f"{class_name}_request: {request}")

        request = TextFormatter.agent_request(request)

        response = await self.agent.ainvoke(request, config=config)
        if isinstance(response, dict):
            result = response["messages"][-1].content
        else:
            result = response

        _LOGGER.info(f"{class_name}_response: {result}")
        state["result"] = result
        state["messages"] = old_messages + [
            HumanMessage(content=result, name="Аналитик")
        ]
        return state

    async def run(self, msg: str, state: PlAgentState, config: dict):
        if "messages" not in state or not state["messages"]:
            await self.create_agent()
            state["task"] = pl_prompt.format(system_requirements=state["task"])
        else:
            state = TextFormatter.add_message(state, msg)
        state = await self.run_agent(state, config)
        response = ResultFormatter.get_result(state)
        response["state"] = state
        return response
