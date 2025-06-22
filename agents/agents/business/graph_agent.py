from settings import llm, graph_maker_prompt
from utils.cutomLogger import customLogger
from langchain.schema import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, List
from typing_extensions import TypedDict

from abstract.abstract_agent import AbstractAgent
from agents.utils.parser import Parser
from agents.utils.text_formatter import TextFormatter
from agents.utils.result_formatter import ResultFormatter


_LOGGER = customLogger.getLogger(__name__)
POSTFIX = "\n\nИсправь, пожалуйста, и сгенерируй граф связей заново."


class GraphAgentState(TypedDict):
    task: str
    description: str
    messages: List
    result: str
    questions: List


class GraphAgent(AbstractAgent):
    def __init__(self):
        self.agent = self.create_agent()

    def create_agent(self):
        agent = create_react_agent(llm, tools=[], checkpointer=MemorySaver())
        return agent

    async def run_agent(self, state: GraphAgentState, config: dict):
        class_name = self.__class__.__name__.lower()
        _LOGGER.info(
            f"Status: {class_name}, thread_id: {config['configurable']['thread_id']}"
        )
        flag: bool = False
        if "questions" in state and state["questions"]:
            flag = True

        if "messages" in state and state["messages"]:
            old_messages = state["messages"]
            request = TextFormatter.question_agent_request(old_messages, POSTFIX, state)
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

        matches = Parser.parse_question(result)
        if matches and not flag:
            questions = TextFormatter.format_questions(matches)
            state["questions"] = "Возникли вопросы:\n" + "\n".join(questions)
        else:
            state["result"] = result
        state["messages"] = old_messages + [
            HumanMessage(content=result, name="Аналитик")
        ]
        return state

    async def run(self, msg: str, state: GraphAgentState, config: dict):
        if "messages" not in state or not state["messages"]:
            state["task"] = graph_maker_prompt.format(
                task=state["task"], description=state["description"]
            )
        else:
            state = TextFormatter.add_message(state, msg)
        state = await self.run_agent(state, config)
        response = ResultFormatter.get_result_mermaid(state)
        response["state"] = state
        return response
