import os
import subprocess
from copy import deepcopy
from pathlib import Path
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader

from agents.tools.script_tools.file_processor import FileProcessor
from settings import CODE_TEMPLATES, templates_dir
from utils.cutomLogger import customLogger

_LOGGER = customLogger.getLogger(__name__)
env = Environment(loader=FileSystemLoader(templates_dir))


class Generator:
    def __init__(self, project_name):
        self.project = project_name
        self.config = deepcopy(CODE_TEMPLATES)

    def get_template(self, template_name):
        return env.get_template(self.config[template_name]["template"])

    def get_template_txt(self, template_name):
        return FileProcessor.read_file(self.config[template_name]["template"])

    def generate_mcp_server(
        self, functions: List[Dict[str, str]], server_name: str, output_file: str
    ) -> None:
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

    def generate_mcp_client(self, tools: Dict[str, str], output_file: str) -> None:
        template_server = self.get_template("TEMPLATE_MCP_CLIENT")
        config_str = template_server.render(tools=tools)
        FileProcessor.save_str(output_file, config_str)
        _LOGGER.info(f"MCP Client записан в файл {output_file}")

    def generate_agent_state(self, agents: List[str], output_file: str) -> None:
        template_state = self.get_template("TEMPLATE_AGENT_STATE")
        state_str = template_state.render(agents=agents)
        FileProcessor.save_str(output_file, state_str)
        _LOGGER.info(f"Agent State записан в файл {output_file}")

    def generate_agent(
        self, agent: str, server_names: List[str], output_file: str
    ) -> None:
        template_state = self.get_template("TEMPLATE_AGENT_CLASS")
        state_str = template_state.render(agent_name=agent, server_names=server_names)
        FileProcessor.save_str(output_file, state_str)
        _LOGGER.info(f"Agent Class записан в файл {output_file}")

    def generate_endpoints(self, agent: str, output_file: str) -> None:
        template = self.get_template("TEMPLATE_ENDPOINTS")
        endpoints_code = template.render(agent_name=agent)
        FileProcessor.save_str(output_file, endpoints_code)
        _LOGGER.info(f"Agent Endpoints записан в файл {output_file}")

    def generate_settings(
        self, agents: List[str], servers: List[str], output_file: str
    ) -> None:
        template = self.get_template("TEMPLATE_SETTINGS")
        settings_code = template.render(agents=agents, servers=servers)
        FileProcessor.save_str(output_file, settings_code)
        _LOGGER.info(f"Settings записан в файл {output_file}")

    def generate_readme(
        self,
        project_path: str,
        output_file: str,
        project_name: str = None,
        project_desc: str = None,
    ) -> None:
        readme_template = self.get_template("TEMPLATE_README")
        result = subprocess.run(["tree", project_path], capture_output=True, text=True)
        tree = result.stdout
        base_path = os.path.basename(project_path)
        tree = tree.replace(project_path, base_path)
        test_desc = "Тестовое описание"
        readme_txt = readme_template.render(
            project_name="TEST_PROJECT", description=test_desc, tree=tree
        )
        FileProcessor.save_str(output_file, readme_txt)
        _LOGGER.info(f"README сгенерирован и сохранен в {output_file}")

    @staticmethod
    def generate_env(functions: List, output_file: str) -> None:
        valid_types = {"get_mcp_template", "post_mcp_template"}
        _functions = []
        for function in functions:
            if function["toolType"] in valid_types:
                url = (function["toolName"] + '_url=""').upper()
                _functions += [url]
        env_str = "\n".join(_functions)
        FileProcessor.save_str(output_file, env_str)
        _LOGGER.info(f"env успешно сгенерирован и записан в {output_file}")

    @staticmethod
    def prepare_params(params: List[str]) -> str:
        return ", ".join(params)

    def generate_graph(self, graph: Dict, output_file: str) -> None:
        template_node = self.get_template("TEMPLATE_GRAPH_NODE")
        macro_module = template_node.make_module()
        agent_node_templates = {
            "agent_with_tools": macro_module.agent_with_tools,
            "agent_orchestrator": macro_module.agent_orchestrator,
        }

        template_graph = self.get_template("TEMPLATE_GRAPH_STRUCTURE")
        initial_state = graph.get("initialState", "")
        agents, directions = [], []
        nodes_code_list = []
        for node in graph.get("nodes", []):
            agent = node.get("name")
            node_name = (
                "agent_orchestrator" if agent == "orchestrator" else "agent_with_tools"
            )
            node_template = agent_node_templates[node_name]
            direction = node.get("to")
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

    def create_project_structure(self, project: str, config: str) -> None:
        endpoints_dir = f"{project}/api"
        models_dir = f"{project}/models"
        agents_dir = f"{project}/services/agents"
        mcp_dir = f"{project}/services/mcp"
        for tmp_dir in [project, endpoints_dir, models_dir, agents_dir, mcp_dir]:
            Path(tmp_dir).mkdir(exist_ok=True, parents=True)
        config = FileProcessor.read_json(config)
        servers = {}
        all_functions = []
        for _server in config.get("servers"):
            functions = [
                {
                    "template": tool["toolType"],
                    "function_name": tool["toolName"],
                    "args": Generator.prepare_params(tool.get("params", [])),
                    "docstring": tool["toolDescription"],
                }
                for tool in _server["tools"]
            ]
            all_functions += _server["tools"]
            server_name = _server["serverName"]
            servers[server_name] = f"{server_name}_mcp_tool"
            mcp_server = f"{mcp_dir}/{server_name}_mcp.py"
            self.generate_mcp_server(functions, server_name, mcp_server)

        mcp_client = f"{mcp_dir}/mcp_client.py"
        self.generate_mcp_client(servers, mcp_client)

        agents, tools_list = [], []
        for _agent in config.get("agents"):
            agent_name = _agent["agentName"]
            tools_list = _agent["servers"]
            agents.append(agent_name)

            tmp_dir = f"{agents_dir}/{agent_name}_agent.py"
            self.generate_agent(agent_name, tools_list, tmp_dir)

        agent_state = f"{agents_dir}/agent_state.py"
        self.generate_agent_state(agents, agent_state)

        endpoints_path = f"{endpoints_dir}/endpoints.py"
        self.generate_endpoints(agents[0], endpoints_path)

        models_path = f"{models_dir}/agents.py"
        model_template = self.get_template_txt("TEMPLATE_MODELS_AGENT")
        FileProcessor.save_str(models_path, model_template)

        main_path = f"{project}/main.py"
        main_template = self.get_template_txt("TEMPLATE_MAIN")
        FileProcessor.save_str(main_path, main_template)

        env_path = f"{project}/.env"
        self.generate_env(all_functions, env_path)

        settings_path = f"{project}/settings.py"
        servers = list(servers.keys())
        self.generate_settings(agents, servers, settings_path)

        graph_path = f"{project}/services/agents/graph.py"
        graph = config.get("graph", dict())
        self.generate_graph(graph, graph_path)

        readme_path = f"{project}/README.md"
        self.generate_readme(project, readme_path)

        req = self.get_template_txt("TEMPLATE_REQUIREMENTS")
        docker = self.get_template_txt("TEMPLATE_DOCKER")
        req_path = f"{project}/requirements.txt"
        docker_path = f"{project}/Dockerfile"
        FileProcessor.save_str(req_path, req)
        FileProcessor.save_str(docker_path, docker)

        _LOGGER.info(f"Проект сгенерирован и сохранен в {project}")
