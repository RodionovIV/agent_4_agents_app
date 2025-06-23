from typing import Dict, List


class ConfigParser:
    @staticmethod
    def prepare_params(params: List[str]) -> str:
        return ", ".join(params)

    @staticmethod
    def parse_tools(tools: List[Dict]) -> List[Dict]:
        functions = [
            {
                "template": tool["toolType"],
                "function_name": tool["toolName"],
                "args": ConfigParser.prepare_params(tool.get("params", [])),
                "docstring": tool["toolDescription"],
            }
            for tool in tools
        ]
        return functions

    @staticmethod
    def get_all_tools(config: Dict) -> List:
        all_functions = []
        for server in config.get("servers", []):
            all_functions += server["tools"]
        return all_functions

    @staticmethod
    def get_server_names(config: Dict) -> List:
        return [server["serverName"] for server in config.get("servers", [])]

    @staticmethod
    def get_agent_names(config: Dict) -> List:
        return [agent["agentName"] for agent in config.get("agents")]
