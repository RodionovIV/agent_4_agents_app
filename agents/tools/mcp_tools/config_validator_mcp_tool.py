import sys
from pathlib import Path

root = Path(__file__).parents[3]
sys.path.insert(0, str(root))

import json
import re
import sys
from json.decoder import JSONDecodeError
from xml.dom import ValidationErr

from mcp.server.fastmcp import FastMCP

from agents.tools.mcp_tools.validator.pydantic_validation import SystemSpec
from utils.cutomLogger import customLogger


def parse_json(s: str):
    match = re.search(r"```json\s*(.*?)\s*```", s, re.DOTALL)
    if match:
        result_str = match.group(1)
        result = json.loads(result_str)
        return result
    else:
        raise JSONDecodeError("Incorrect JSON")


_LOGGER = customLogger.getLogger(__name__)


mcp = FastMCP("config", port="8001")


@mcp.tool()
def check_config(config_file):
    """
    Use this tool to check the generated config for correctness.
    """
    _LOGGER.info(f" ! check_config tool with config {str(config_file)}")
    result = "CONFIG INVALID. Check format."
    try:
        file = parse_json(config_file)
        spec = SystemSpec(**file)
        result = "CONFIG VALID"
        _LOGGER.info(result)
    except ValidationErr as e:
        result = f"Validation failed: {e}"
        _LOGGER.info(result)
    except JSONDecodeError as e:
        result = f"Incorrect JSON. Check it."
        _LOGGER.info(result)
    except SyntaxError as e:
        result = f"Request failed: config must contain ```json. {e}"
        _LOGGER.info(result)
    except Exception as e:
        result = f"Validation failed: {e}"
        _LOGGER.info(result)
    finally:
        return result


if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    mcp.run(transport=transport)
