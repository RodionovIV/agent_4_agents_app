import os
import subprocess
from copy import deepcopy
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader

from agents.tools.script_tools.agent_config_parser import ConfigParser
from agents.tools.script_tools.file_processor import FileProcessor
from settings import CODE_TEMPLATES, git_repo, templates_dir
from utils.cutomLogger import customLogger

_LOGGER = customLogger.getLogger(__name__)
env = Environment(loader=FileSystemLoader(templates_dir))


class Generator:
    def __init__(self, project_name, agent_config):
        self.project = os.path.join(git_repo, project_name)
        self.config = deepcopy(CODE_TEMPLATES)
        self.agent_config = agent_config

    def get_template(self, template_name):
        return env.get_template(self.config[template_name]["template"])

    def get_template_txt(self, template_name):
        return FileProcessor.read_file(self.config[template_name]["template"])

    def get_path(self, template_name, kwargs=None):
        if not kwargs:
            kwargs = dict()
        kwargs["project"] = self.project
        return self.config[template_name]["path"].format(**kwargs)

    def generate_mcp_server(
        self, functions: List[Dict[str, str]], server_name: str
    ) -> None:
        output_file = self.get_path(
            "TEMPLATE_MCP_SERVER", kwargs={"server_name": server_name}
        )
        template_tools = self.get_template("TEMPLATE_MCP_TOOLS")
        template_server = self.get_template("TEMPLATE_MCP_SERVER")

        macro_module = template_tools.make_module()

        get_mcp_template = macro_module.get_mcp_template
        post_mcp_template = macro_module.post_mcp_template
        templates = {
            "get_mcp_template": get_mcp_template,
            "post_mcp_template": post_mcp_template,
        }

        # Для кода
        tools_code = "\n\n".join(
            [
                templates[f["template"]](
                    f["function_name"], f["docstring"], f.get("args", "")
                )
                for f in functions
            ]
        )
        server_code = template_server.render(
            server_name=server_name, tools_code=tools_code
        )
        # Запись в файл
        FileProcessor.save_str(output_file, server_code)

        _LOGGER.info(f"MCP Server успешно записан в {output_file}")

    def generate_mcp_client(self, tools: Dict[str, str]) -> None:
        template_name = "TEMPLATE_MCP_CLIENT"
        output_file = self.get_path(template_name)
        template_server = self.get_template(template_name)
        config_str = template_server.render(tools=tools)
        FileProcessor.save_str(output_file, config_str)
        _LOGGER.info(f"MCP Client записан в файл {output_file}")

    def generate_mcp(self):
        config = self.agent_config
        servers = {}
        for _server in config.get("servers", []):
            tools = _server["tools"]
            functions = ConfigParser.parse_tools(tools)
            server_name = _server["serverName"]
            servers[server_name] = f"{server_name}_mcp_tool"
            self.generate_mcp_server(functions, server_name)
        self.generate_mcp_client(servers)

    def generate_agent_state(self, agents: List[str]) -> None:
        template_name = "TEMPLATE_AGENT_STATE"
        output_file = self.get_path(template_name)
        template_state = self.get_template(template_name)
        state_str = template_state.render(agents=agents)
        FileProcessor.save_str(output_file, state_str)
        _LOGGER.info(f"Agent State записан в файл {output_file}")

    def generate_agent(self, agent_name: str, server_names: List[str]) -> None:
        template_name = "TEMPLATE_AGENT_CLASS"
        output_file = self.get_path(template_name, kwargs={"agent_name": agent_name})
        template_state = self.get_template(template_name)
        state_str = template_state.render(
            agent_name=agent_name, server_names=server_names
        )
        FileProcessor.save_str(output_file, state_str)
        _LOGGER.info(f"Agent Class записан в файл {output_file}")

    def generate_agents(self) -> None:
        config = self.agent_config
        agents, tools_list = [], []
        for _agent in config.get("agents"):
            agent_name = _agent["agentName"]
            tools_list = _agent["servers"]
            agents.append(agent_name)
            self.generate_agent(agent_name, tools_list)

        self.generate_agent_state(agents)

    def generate_endpoints(self) -> None:
        template_name = "TEMPLATE_ENDPOINTS"
        output_file = self.get_path(template_name)
        template = self.get_template(template_name)
        endpoints_code = template.render()
        FileProcessor.save_str(output_file, endpoints_code)
        _LOGGER.info(f"Agent Endpoints записан в файл {output_file}")

    def generate_settings(self) -> None:
        template_name = "TEMPLATE_SETTINGS"
        output_file = self.get_path(template_name)
        template = self.get_template(template_name)
        agents = ConfigParser.get_agent_names(self.agent_config)
        servers = ConfigParser.get_server_names(self.agent_config)
        settings_code = template.render(agents=agents, servers=servers)
        FileProcessor.save_str(output_file, settings_code)
        _LOGGER.info(f"Settings записан в файл {output_file}")

    def generate_readme(self) -> None:
        project_path = self.project
        template_name = "TEMPLATE_README"
        output_file = self.get_path(template_name)
        readme_template = self.get_template(template_name)
        result = subprocess.run(["tree", project_path], capture_output=True, text=True)
        tree = result.stdout
        base_path = os.path.basename(project_path)
        tree = tree.replace(project_path, base_path)
        desc = self.agent_config.get("projectDesc", "")
        project_name = self.agent_config.get("projectName", "")
        readme_txt = readme_template.render(
            project_name=project_name, description=desc, tree=tree
        )
        FileProcessor.save_str(output_file, readme_txt)
        _LOGGER.info(f"README сгенерирован и сохранен в {output_file}")

    def generate_env(self) -> None:
        template_name = "TEMPLATE_ENV"
        output_file = self.get_path(template_name)
        functions = ConfigParser.get_all_tools(self.agent_config)
        valid_types = {"get_mcp_template", "post_mcp_template"}
        _functions = []
        for function in functions:
            if function["toolType"] in valid_types:
                url = (function["toolName"] + '_url=""').upper()
                _functions += [url]
        env_str = "\n".join(_functions)
        FileProcessor.save_str(output_file, env_str)
        _LOGGER.info(f"env успешно сгенерирован и записан в {output_file}")

    def generate_graph(self) -> None:
        output_file = self.get_path("TEMPLATE_GRAPH_STRUCTURE")
        template_graph = self.get_template("TEMPLATE_GRAPH_STRUCTURE")
        template_node = self.get_template("TEMPLATE_GRAPH_NODE")
        macro_module = template_node.make_module()
        agent_node_templates = {
            "agent_with_tools": macro_module.agent_with_tools,
            "agent_orchestrator": macro_module.agent_orchestrator,
        }
        graph = self.agent_config.get("graph", dict())
        initial_state = graph.get("initialState", "")
        agents, directions = [], []
        nodes_code_list = []
        for node in graph.get("nodes", []):
            agent = node.get("name")
            direction = node.get("to")
            if agent == "orchestrator":
                node_name = "agent_orchestrator"
                direction = [x.strip() for x in direction.split(",")]
            else:
                node_name = "agent_with_tools"
            node_template = agent_node_templates[node_name]

            node_str = node_template(agent, direction)

            nodes_code_list += [node_str]
            agents += [agent]
            directions += [direction]

        nodes_code = "\n\n".join(nodes_code_list)
        graph_code = template_graph.render(
            agents=agents, nodes_code=nodes_code, initial_state=initial_state
        )
        FileProcessor.save_str(output_file, graph_code)
        _LOGGER.info(f"Agent Graph успешно записан в {output_file}")

    def _generate_text_template(self, template_name):
        output_file = self.get_path(template_name)
        template_text = self.get_template_txt(template_name)
        FileProcessor.save_str(output_file, template_text)

    def generate_requiremets(self):
        template_name = "TEMPLATE_REQUIREMENTS"
        self._generate_text_template(template_name)

    def generate_docker_file(self):
        template_name = "TEMPLATE_DOCKER"
        self._generate_text_template(template_name)

    def generate_main(self):
        template_name = "TEMPLATE_MAIN"
        self._generate_text_template(template_name)

    def generate_models_agent(self):
        template_name = "TEMPLATE_MODELS_AGENT"
        self._generate_text_template(template_name)

    def generate(self) -> None:
        self.generate_mcp()
        self.generate_graph()
        self.generate_agents()

        self.generate_endpoints()
        self.generate_models_agent()
        self.generate_env()
        self.generate_settings()
        self.generate_readme()
        self.generate_requiremets()
        self.generate_docker_file()
        self.generate_main()

        _LOGGER.info(f"Проект сгенерирован и сохранен в {self.project}")
