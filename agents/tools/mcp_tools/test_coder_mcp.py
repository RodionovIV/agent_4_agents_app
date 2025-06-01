from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from pathlib import Path
import os, re, sys
import logging

_LOGGER = logging.getLogger(__name__)

from pydantic import BaseModel, Field

class SaveResult(BaseModel):
    status: str = Field(description="Статус сохранения файла")
    message: str = Field(description="Сообщение о результате сохранения в файл")

class ReadResult(BaseModel):
    status: str = Field(description="Статус чтения файла")
    message: str = Field(description="Сообщение о результате чтения файла")
    result: str = Field(description="Содержимое файла")

class MkdirResult(BaseModel):
    status: str = Field(description="Статус создания директории")
    message: str = Field(description="Сообщение о результате создания директории")

class PythonResult(BaseModel):
    status: str = Field(description="Статус запуска Python-кода")
    message: str = Field(description="Сообщение о результате запуска Python-кода.")

_LOGGER = logging.getLogger(__name__)


mcp = FastMCP("coder")

# @mcp.tool()
# def read_plan():
#     """
#     Use this tool to read plan of your development.
#     """
#     _LOGGER.info(f" ! read_plan")
#     with open("plan_cool.md", "r") as f:
#         return f.read()

@mcp.tool()
def save_file(file_path:str, content:str) -> SaveResult:
    """Use this tool to save the result to a file. If you can't write to the file, first create the file and then write the contents to it."""
    _LOGGER.info(f"! save_file to {file_path}, content: {content}")
    try:
        match_python = re.search(r'```python\s*(.*?)\s*```', content, re.DOTALL)
        if match_python:
            content = match_python.group(1)
        with open(file_path, "w") as f:
            f.write(content)
        return SaveResult(status="OK", message="Файл успешно сохранен!")
    except Exception as e:
        return SaveResult(status="FAIL", message=f"Не удалось сохранить файл, ошибка: {e}")

@mcp.tool()
def read_file(file_path: str) -> ReadResult:
    """Use this tool to read information from a file."""
    _LOGGER.info(f"! read_file from {file_path}")
    try:
        with open(file_path, "r") as f:
            content = f.read()
        if file_path.endswith(".py"):
            content = (
                "```python\n"
                f"{content}"
                "\n```")
        return ReadResult(status="OK", message="Файл успешно прочитан!", result=content)
    except Exception as e:
        return ReadResult(status="FAIL", message=f"Не удалось прочитать файл, ошибка: {e}", result=None)

@mcp.tool()
def create_dir(path: str) -> MkdirResult:
    """Use this tool to create a directory."""
    _LOGGER.info(f"! create_dir {path}")
    try:
        if Path(path).exists():
            return MkdirResult(status="OK", message="Директория уже существует!")
        Path(path).mkdir(parents=True, exist_ok=True)
        return MkdirResult(status="OK", message="Директория успешно создана!")
    except:
        return MkdirResult(status="FAIL", message="Не удалось создать директорию")

@mcp.tool()
def run_python_code(code_str: str) -> PythonResult:
    """Use this tool to run Python code."""
    _LOGGER.info(f"! run_python_code {code_str}")
    try:
        match_python = re.search(r'```python\s*(.*?)\s*```', code_str, re.DOTALL)
        if match_python:
            code = match_python.group(1)
            result = exec(code)
        else:
            return PythonResult(status="FAIL", message="Не удалось выделить информацию из блока ```python[code]```.")
        return PythonResult(status="OK", message=f"Код успешно запущен! Результат: {result}")
    except Exception as e:
        return PythonResult(status="FAIL", message=f"Не удалось запустить код, ошибка: {e}")

if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    mcp.run(transport=transport)