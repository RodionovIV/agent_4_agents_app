from typing import List, TypedDict
from uuid import uuid4

from langchain.schema import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

import settings
from agents.tools.mcp_tools.tools import client
from agents.tools.script_tools.generator import Generator
from agents.utils.parser import Parser
from agents.utils.text_formatter import TextFormatter
from settings import (config_example_orchestrator, config_example_workflow,
                      config_prompt, config_specification, git_prompt, llm)
from utils.cutomLogger import customLogger

_LOGGER = customLogger.getLogger(__name__)

POSTFIX = "\n\nИсправь, пожалуйста, и сгенерируй код полностью заново."


class CoAgentState(TypedDict):
    task: str
    config_task: str
    git_task: str
    config_result: str
    git_result: str
    messages: List
    repo_name: str


class CoAgent:
    def __init__(self):
        pass

    async def create(self):
        config_tools = await client.get_tools(server_name="config")
        git_tools = await client.get_tools(server_name="git")

        self.config_agent = create_react_agent(
            llm, config_tools, checkpointer=MemorySaver()
        )

        self.git_agent = create_react_agent(llm, git_tools, checkpointer=MemorySaver())

    async def run_config_agent(self, state: CoAgentState, config: dict):
        class_name = self.__class__.__name__.lower() + "_config"
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
        response = await self.config_agent.ainvoke(request, config=config)

        if isinstance(response, dict):
            result = response["messages"][-1].content
        else:
            result = response
        _LOGGER.info(f"{class_name}_response: {result}")

        matches = Parser.parse_question(result)
        if matches:
            questions = TextFormatter.format_questions(matches)
            state["questions"] = "Возникли вопросы:\n" + "\n".join(questions)
        else:
            state["config_result"] = result
        state["messages"] = old_messages + [
            HumanMessage(content=result, name="Аналитик")
        ]
        return state

    async def run_git_agent(self, state: CoAgentState):
        class_name = self.__class__.__name__.lower() + "_git"
        _LOGGER.info(f"Status: {class_name}")
        git_config = {
            "configurable": {"thread_id": str(uuid4())},
            "recursion_limit": 100,
        }
        request = state["git_task"]
        request = TextFormatter.agent_request(request)

        response = await self.git_agent.ainvoke(request, config=git_config)
        if isinstance(response, dict):
            result = response["messages"][-1].content
        else:
            result = response
        _LOGGER.info(f"{class_name}_response: {result}")
        state["git_result"] = result
        return state

    async def run_agent(self, state: CoAgentState, config: dict):
        state = await self.run_config_agent(state, config)
        agent_config = Parser.parse_json(state["config_result"])
        project_name = state["repo_name"]
        generator = Generator(project_name, agent_config)
        generator.generate()
        state = await self.run_git_agent(state)
        return state

    async def run(self, msg: str, state: CoAgentState, config: dict):
        if "messages" not in state or not state["messages"]:
            await self.create()
            state["config_task"] = config_prompt.format(
                json_spec=str(config_specification),
                description=state["task"],
                workflow_example=str(config_example_workflow),
                orchestrator_example=str(config_example_orchestrator),
            )
            state["git_task"] = git_prompt.format(
                git_repo=settings.git_repo, project_name=state["repo_name"]
            )
        else:
            state = TextFormatter.add_message(state, msg)
        await self.run_agent(state, config)
        return {"status": "OK"}
