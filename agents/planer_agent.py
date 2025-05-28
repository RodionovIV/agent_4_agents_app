# Create server parameters for stdio connection
from utils.cutomLogger import customLogger
import asyncio
from uuid import uuid4
import os
import sys
import io

from dotenv import find_dotenv, load_dotenv
from langchain_gigachat.chat_models.gigachat import GigaChat
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.client import MultiServerMCPClient
from rich import print as rprint

import locale
term_encoding = locale.getpreferredencoding(False)
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="cp1251")


_LOGGER = customLogger.getLogger(__name__)
POSTFIX = "\n\nИсправь, пожалуйста, и сгенерируй описание заново."

# LLM GigaChat
model = GigaChat(model="GigaChat-2-Max",
                 verify_ssl_certs=False,
                 streaming=False,
                 max_tokens=8000,
                 timeout=600)