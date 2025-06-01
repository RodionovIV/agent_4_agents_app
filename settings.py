from langchain_gigachat.chat_models import GigaChat

import os
base_dir = os.path.dirname(os.path.abspath(__file__))
save_dir = base_dir + "/tmp"
puppeteer_config = base_dir + "/configs/puppeteer-config.json"
tools_dir = base_dir + "/agents/tools/mcp_tools/"

# MCP Tools
planer_mcp_tool = tools_dir + "test_planer_mcp.py"
coder_mcp_tool = tools_dir + "test_coder_mcp.py"
git_mcp_tool = tools_dir + "test_git_mcp.py"
############


LOG_FILE = "app.log"


def __read_doc(path):
    with open(path, mode="r") as f:
        return f.read()
DESC_PROMPT_PATH = "prompts/desc_prompt.txt"
DESC_INSTRUMENTS_PATH = "instructions/desc_instruments.txt"

GRAPH_PROMPT_PATH = "prompts/graph_prompt.txt"

BA_INSTRUCTION_PATH = "instructions/ba_instruction.md"
BA_PROMPT_PATH = "prompts/ba_prompt.txt"

SA_INSTRUCTION_PATH = "instructions/sa_instruction.md"
SA_PROMPT_PATH = "prompts/sa_prompt.txt"

PL_PROMPT_PATH = "prompts/planer_prompt.txt"
CODER_PROMPT_PATH = "prompts/coder_prompt.txt"
GIT_PROMPT_PATH = "prompts/git_prompt.txt"

graph_maker_prompt = __read_doc(GRAPH_PROMPT_PATH)

describer_prompt = __read_doc(DESC_PROMPT_PATH)
instruments = __read_doc(DESC_INSTRUMENTS_PATH)

ba_instruction = __read_doc(BA_INSTRUCTION_PATH)
ba_prompt = __read_doc(BA_PROMPT_PATH)

sa_instruction = __read_doc(SA_INSTRUCTION_PATH)
sa_prompt = __read_doc(SA_PROMPT_PATH)

pl_prompt = __read_doc(PL_PROMPT_PATH)
coder_prompt = __read_doc(CODER_PROMPT_PATH)
git_prompt = __read_doc(GIT_PROMPT_PATH)

llm = GigaChat(
    model="GigaChat-2-Max",
    verify_ssl_certs=False,
    profanity_check=False,
    streaming=False,
    max_tokens=8192,
    temperature=0.3,
    repetition_penalty=1.01,
    timeout=180
)

# UI Settings
LOGO_FILE = "src/devil_2_without.png"
SAVE_PATH = "tmp/test.md"
BAR_STEP = 17

# from pydantic import BaseModel
#
# class State:
#     header: str
#     button: str
#     response_status: str
#     next_task: str

# Status Logic
HEADER_STATUS = {
    "DESC": "📝 Генерация описания",
    "GRAPH": "🌐 Генерация графа взаимодействия",
    "BA": "📊 Генерация бизнес-требований",
    "SA": "🧠 Генерация системных требований",
    "PL": "🪄 Составить план разработки",
    "CO": "💻 Сгенерировать код"
}

BUTTON_STATUS = {
    "DESC": "Следующий шаг -> 🌐 Граф взаимодействий",
    "GRAPH": "Следующий шаг -> 📊 Бизнес-анализ",
    "BA": "Следующий шаг -> 🧠 Системный анализ",
    "SA": "Следующий шаг -> 🪄 План разработки",
    "PL": "Следующий шаг -> 💻 Генерация кода",
    "CO": "✅ Закончить",
}

NEXT_STATUS_LIST = ["GRAPH", "BA", "SA", "PL", "CO"]

RESPONSE_STATUS = {
    "DESC": "Описание успешно сгенерировано",
    "GRAPH": "Граф связей построен",
    "BA": "Бизнес-требования сгенерированы",
    "SA": "Системные требования сгенерированы",
    "PL": "План разработки составлен",
    "CO": "Код сгенерирован и запушен в https://github.com/RodionovIV/agent-sandbox/tree/main/{project_name}"
}

NEXT_TASK = {
    "GRAPH": "Переходим на этап построения графа связей",
    "BA": "Переходим на этап генерации бизнес-требований",
    "SA": "Переходим на этап генерации системных требований",
    "PL": "Переходим на этап генерации плана разработки",
    "CO": "Переходим на этап генерации кода"
}

REQUIRED_MSGS = {
    "GRAPH": "Для генерации графа связей необходимо ввести описание процесса",
    "BA": "Для генерации бизнес-требований необходимо ввести описание процесса",
    "SA": "Для генерации системных требований необходимо ввести описание процесса",
    "PL": "Для генерации плана разработки необходимо ввести описание процесса",
    "CO": "Для генерации кода необходимо ввести план разработки",
}

WATEMARK = "\n\n*Сгенерировано GigaChat-Max-2*"