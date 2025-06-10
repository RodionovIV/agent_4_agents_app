import settings

from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "planer": {
            "transport": "stdio",
            "command": "python",
            "args": [settings.planer_mcp_tool]
        },
        "coder": {
            "transport": "stdio",
            "command": "python",
            "args": [settings.coder_mcp_tool]
        },
        "git": {
            "transport": "stdio",
            "command": "python",
            "args": [settings.git_mcp_tool]
        }
    },
)