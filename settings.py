import json
import os

from dotenv import load_dotenv

from llm.client import LLM

load_dotenv()

base_dir = os.path.dirname(os.path.abspath(__file__))
save_dir = base_dir + "/tmp"
puppeteer_config = base_dir + "/configs/puppeteer-config.json"
code_config = base_dir + "/configs/code-template-config.json"
n8n_config = base_dir + "/configs/n8n.json"
n8n_result_template = base_dir + "/configs/n8n_result_template.json"
tools_dir = base_dir + "/agents/tools/mcp_tools/"
templates_dir = base_dir + "/templates"

# MCP Tools
config_mcp_tool = tools_dir + "config_validator_mcp_tool.py"
planer_mcp_tool = tools_dir + "test_planer_mcp.py"
coder_mcp_tool = tools_dir + "test_coder_mcp.py"
git_mcp_tool = tools_dir + "test_git_mcp.py"
############


LOG_FILE = "app.log"


def __read_doc(path):
    with open(path, mode="r") as f:
        return f.read()


def __read_json(path):
    with open(path, mode="r") as f:
        return json.load(f)


def __full_path(path):
    return os.path.join(base_dir, path)


CODE_TEMPLATES = {
    k: {
        "template": v["template"]
        if v["template"].endswith(".jinja2")
        else os.path.join(templates_dir, v["template"]),
        "path": v["path"],
    }
    for k, v in __read_json(code_config).items()
}
DESC_PROMPT_PATH = __full_path("prompts/business/desc_prompt.txt")
DESC_INSTRUMENTS_PATH = __full_path("instructions/desc_instruments.txt")

GRAPH_PROMPT_PATH = __full_path("prompts/business/graph_prompt.txt")

BA_INSTRUCTION_PATH = __full_path("instructions/ba_instruction.md")
BA_PROMPT_PATH = __full_path("prompts/business/ba_prompt.txt")

SA_INSTRUCTION_PATH = __full_path("instructions/sa_instruction.md")
SA_PROMPT_PATH = __full_path("prompts/business/sa_prompt.txt")

CONFIG_SPECIFICATION_PATH = __full_path("instructions/config_specification.json")
CONFIG_EXAMPLE_WORKFLOW_PATH = __full_path("instructions/config_workflow_example.json")
CONFIG_EXAMPLE_ORCHESTRATOR_PATH = __full_path(
    "instructions/config_orchestrator_example.json"
)
CONFIG_PROMPT_PATH = __full_path("prompts/code/config_generator_prompt.txt")

PL_PROMPT_PATH = __full_path("prompts/code/planer_prompt.txt")
CODER_PROMPT_PATH = __full_path("prompts/code/coder_prompt.txt")
GIT_PROMPT_PATH = __full_path("prompts/code/git_prompt.txt")
PROMPT_GENERATOR_PATH = __full_path("prompts/code/prompt_generator.txt")

graph_maker_prompt = __read_doc(GRAPH_PROMPT_PATH)

describer_prompt = __read_doc(DESC_PROMPT_PATH)
instruments = __read_doc(DESC_INSTRUMENTS_PATH)

ba_instruction = __read_doc(BA_INSTRUCTION_PATH)
ba_prompt = __read_doc(BA_PROMPT_PATH)

sa_instruction = __read_doc(SA_INSTRUCTION_PATH)
sa_prompt = __read_doc(SA_PROMPT_PATH)

config_specification = __read_json(CONFIG_SPECIFICATION_PATH)
config_example_orchestrator = __read_json(CONFIG_EXAMPLE_ORCHESTRATOR_PATH)
config_example_workflow = __read_json(CONFIG_EXAMPLE_WORKFLOW_PATH)
config_n8n = __read_json(n8n_config)
result_n8n = __read_json(n8n_result_template)
config_prompt = __read_doc(CONFIG_PROMPT_PATH)

pl_prompt = __read_doc(PL_PROMPT_PATH)
coder_prompt = __read_doc(CODER_PROMPT_PATH)
git_prompt = __read_doc(GIT_PROMPT_PATH)
prompt_generator_prompt = __read_doc(PROMPT_GENERATOR_PATH)
git_repo = "/app/sandbox"  # os.getenv("SANDBOX_REPO")

llm = LLM.gigachat()

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
    "CO": "💻 Сгенерировать код",
}

BUTTON_STATUS = {
    "DESC": "Следующий шаг -> 📊 Бизнес-анализ",
    "GRAPH": "Следующий шаг -> 🧠 Системный анализ",
    "BA": "Следующий шаг -> 🌐 Граф взаимодействий",
    "SA": "Следующий шаг -> 🪄 План разработки",
    "PL": "Следующий шаг -> 💻 Генерация кода",
    "CO": "✅ Закончить",
}

STATUS_LIST = ["DESC", "BA", "GRAPH", "SA", "PL", "CO"]
NEXT_STATUS_LIST = STATUS_LIST[1:]

RESPONSE_STATUS = {
    "DESC": "Описание успешно сгенерировано",
    "GRAPH": "Граф связей построен",
    "BA": "Бизнес-требования сгенерированы",
    "SA": "Системные требования сгенерированы",
    "PL": "План разработки составлен",
    "CO": (
        "Статус: {response}\n\n"
        "Репозиторий: \n"
        '<a href="https://github.com/RodionovIV/{project_name}" target="_blank">'
        "https://github.com/RodionovIV/{project_name}</a>"
    ),
}

NEXT_TASK = {
    "GRAPH": "Переходим на этап построения графа связей",
    "BA": "Переходим на этап генерации бизнес-требований",
    "SA": "Переходим на этап генерации системных требований",
    "PL": "Переходим на этап генерации плана разработки",
    "CO": "Переходим на этап генерации кода",
}

REQUIRED_MSGS = {
    "GRAPH": "Для генерации графа связей необходимо ввести описание процесса",
    "BA": "Для генерации бизнес-требований необходимо ввести описание процесса",
    "SA": "Для генерации системных требований необходимо ввести описание процесса",
    "PL": "Для генерации плана разработки необходимо ввести описание процесса",
    "CO": "Для генерации кода необходимо ввести план разработки",
}

WATEMARK = "\n\n*Сгенерировано GigaChat-Max-2*"
