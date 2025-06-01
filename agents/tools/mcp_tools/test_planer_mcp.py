import os, sys


from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from pathlib import Path
import re
import logging

_LOGGER = logging.getLogger(__name__)


mcp = FastMCP("planer", port="8001")

@mcp.tool()
def read_instruction(filename):
    """
    Use this tool for read instruction and make decisions.
    Choose correct instruction from list and read it.
    After that make final decision.
    List of instructions:
    "instructions/project_instruction.md" - Instructions for describing the repository structure.
    "instructions/project_content.md" - Instructions for describing each component of the system.
    "instructions/project_agent_instruction.md" - Instructions for describing the llm agent.
    "instructions/project_agent_tools.md" - Instructions for describing tools for an LLM agent.
    """
    _LOGGER.info(f" ! read_instruction with argument {filename}")
    with open(filename, "r") as f:
        str = f.read()
        _LOGGER.info(str)
        return str

# @mcp.tool()
# def write_plan(plan):
#     """
#     Use this tool to plan your development.
#     Carefully study the instructions and identify the system elements that you will need to solve your problem.
#     Next, make a development plan for the developer.
#     Describe in detail the steps that need to be made to each component of the system.
#     Write down the result of your thoughts in a file.
#     """
#     print(f" ! write_plan")
#     with open("plan_cool.md", "w") as f:
#         return f.write(plan)

if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    mcp.run(transport=transport)