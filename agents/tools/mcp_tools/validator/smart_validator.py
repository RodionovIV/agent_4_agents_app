from typing import Dict, Set, List


class SmartValidator:
    @staticmethod
    def get_server_set(config: Dict) -> Set[str]:
        return set([server["serverName"] for server in config["servers"]])

    @staticmethod
    def get_servers_from_agents(config: Dict) -> Set[str]:
        servers = []
        for agent in config["agents"]:
            servers += agent["servers"]
        return servers

    @staticmethod
    def get_agent_names(config: Dict) -> Set[str]:
        return set([agent["agentName"] for agent in config["agents"]])

    @staticmethod
    def validate_node(name: str):
        if "," in name:
            raise ValueError("The name field must not contain ','")

    @staticmethod
    def get_agents_from_graph(config: Dict) -> tuple:
        nodes = config["graph"]["nodes"]
        nodes_from, nodes_to = [], []
        for node in nodes:
            SmartValidator.validate_node(node["name"])
            nodes_from += [node["name"]]
            nodes_to += [x.strip() for x in node["to"].split(",")]
        if "END" not in nodes_to:
            raise ValueError("Nodes do not contain an END")
        if "END" in nodes_from:
            raise ValueError("END is not an agent and should not be contained in the 'name' field of the graph node.")
        return nodes_to, nodes_from

    @staticmethod
    def get_initial_state(config: Dict) -> str:
        return config["graph"]["initialState"]

    @staticmethod
    def validate_tools(config: Dict):
        servers_set = SmartValidator.get_server_set(config)
        for agent in config["agents"]:
            agent_name = agent["agentName"]
            agent_servers = agent["servers"]
            for server in agent_servers:
                if server not in servers_set:
                    raise ValueError(f"Agent {agent_name} contains a server {server} that is not declared in the 'servers' field")

        agent_servers_list = SmartValidator.get_servers_from_agents(config)
        for server_name in list(servers_set):
            if server_name not in agent_servers_list:
                raise ValueError(f"Servername {server_name} is not used by any agent")

    @staticmethod
    def validate_agents(config: Dict):
        agents = SmartValidator.get_agent_names(config)
        agents_to, agents_from = SmartValidator.get_agents_from_graph(config)
        initial_state = SmartValidator.get_initial_state(config)

        for agent in list(agents):
            if agent not in agents_from and agent not in agents_to:
                raise ValueError(f"The agent {agent} is not contained in the graph nodes.")

        for agent in agents_from:
            if agent not in agents:
                raise ValueError(f"The agent {agent} declared in the graph nodes is not included in the agent list.")

        for agent in agents_to:
            if agent == "END":
                continue
            if agent not in agents:
                raise ValueError(f"The agent {agent} declared in the graph nodes is not included in the agent list.")

        if initial_state not in agents:
            raise ValueError(f"Initial state {initial_state} of the graph must be agent")

    @staticmethod
    def validate_config(config: Dict):
        SmartValidator.validate_tools(config)
        SmartValidator.validate_agents(config)
