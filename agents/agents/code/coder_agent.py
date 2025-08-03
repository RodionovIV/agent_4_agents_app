import settings as s
from agents.agents.code.config_agent import ConfigAgent
from agents.agents.code.git_agent import GitAgent
from agents.agents.code.prompt_agent import PromptAgent
from agents.agents.states import CoAgentState
from agents.tools.script_tools.generator import Generator
from agents.tools.script_tools.prompt_processor import PromptProcessor
from agents.utils.parser import Parser
from agents.utils.text_formatter import TextFormatter
from agents.tools.script_tools.vc.github import VersionControl
from utils.cutomLogger import customLogger

_LOGGER = customLogger.getLogger(__name__)


class CoAgent:
    def __init__(self):
        self.config_agent = ConfigAgent()
        self.git_agent = GitAgent()
        self.prompt_agent = PromptAgent()

    async def create(self):
        await self.config_agent.create()
        await self.git_agent.create()

    async def run_agent(self, state: CoAgentState, config: dict):
        state = await self.config_agent.run_agent(state, config)
        agent_config = Parser.parse_json(state["config_result"])
        agent_tasks = PromptProcessor.generate(state["desc"], agent_config)
        agent_prompts = await self.prompt_agent.run(agent_tasks)
        agent_config = PromptProcessor.add_prompts_to_config(
            agent_prompts, agent_config
        )
        project_name = state["repo_name"]
        generator = Generator(project_name, agent_config)
        version_control = VersionControl()
        files = generator.generate()
        await version_control.run(project_name, files)
        state["git_result"] = "SUCCESS"
        # state = await self.git_agent.run_agent(state)
        return state

    async def run(self, msg: str, state: CoAgentState, config: dict):
        if "messages" not in state or not state["messages"]:
            await self.create()
            state["config_task"] = s.config_prompt.format(
                json_spec=str(s.config_specification),
                description=state["task"],
                workflow_example=str(s.config_example_workflow),
                orchestrator_example=str(s.config_example_orchestrator),
            )
            state["git_task"] = s.git_prompt.format(
                git_repo=s.git_repo, project_name=state["repo_name"]
            )
        else:
            state = TextFormatter.add_message(state, msg)
        state = await self.run_agent(state, config)
        return state["git_result"]
