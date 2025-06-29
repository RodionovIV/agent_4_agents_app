from typing import Dict, List

from settings import prompt_generator_prompt


class PromptProcessor:
    @staticmethod
    def get_server_tools(server_name: str, config: Dict) -> List[str]:
        server_desc = []
        for server in config["servers"]:
            if server_name == server["serverName"]:
                for tool in server["tools"]:
                    server_desc.append(tool["toolDescription"])
        return server_desc

    @staticmethod
    def get_tools_desc(agent, config: Dict) -> str:
        tool_desc_list = []
        servers = agent["servers"]
        for server_name in servers:
            tool_desc_list += PromptProcessor.get_server_tools(server_name, config)
        tools = [f"{i + 1}. {tool}" for i, tool in enumerate(tool_desc_list)]
        return "\n".join(tools)

    @staticmethod
    def create_prompt_task(agent_desc: str, desc: str, tools: str) -> str:
        return prompt_generator_prompt.format(
            agent_description=agent_desc, description=desc, tools=tools
        )

    @staticmethod
    def generate(desc: str, config: Dict) -> Dict[str, Dict[str, str]]:
        result = {}
        for agent in config["agents"]:
            tools = PromptProcessor.get_tools_desc(agent, config)
            agent_desc = agent["agentDescription"]
            agent_name = agent["agentName"]
            result[agent_name] = {
                "task": PromptProcessor.create_prompt_task(agent_desc, desc, tools)
            }
        return result

    @staticmethod
    def add_prompts_to_config(agent_prompts: Dict, config: Dict) -> Dict:
        agents = config["agents"]
        n = len(agents)
        for i in range(n):
            agent_name = agents[i]["agentName"]
            config["agents"][i]["agentPrompt"] = agent_prompts[agent_name]["result"]
        return config
