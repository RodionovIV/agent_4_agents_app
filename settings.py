from langchain_gigachat.chat_models import GigaChat

import os
os.environ["GIGACHAT_CREDENTIALS"] = "Yjc1YWZhNTItMzYwYS00NmU4LTk4YjctZjU4YzAwMDIyMGJmOjJhNWE3YmVhLTAyYzctNGJhNy05NWE3LWEzY2YwNGQzYzZiNw=="
base_dir = os.path.dirname(os.path.abspath(__file__))


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

graph_maker_prompt = __read_doc(GRAPH_PROMPT_PATH)

describer_prompt = __read_doc(DESC_PROMPT_PATH)
instruments = __read_doc(DESC_INSTRUMENTS_PATH)

ba_instruction = __read_doc(BA_INSTRUCTION_PATH)
ba_prompt = __read_doc(BA_PROMPT_PATH)

sa_instruction = __read_doc(SA_INSTRUCTION_PATH)
sa_prompt = __read_doc(SA_PROMPT_PATH)


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

# Status Logic
HEADER_STATUS = {
    "DESC": "📝 Генерация описания",
    "GRAPH": "🌐 Генерация графа взаимодействия",
    "BA": "📊 Генерация бизнес-требований",
    "SA": "🧠 Генерация системных требований",
}

BUTTON_STATUS = {
    "DESC": "Следующий шаг -> 🌐 Граф взаимодействий",
    "GRAPH": "Следующий шаг -> 📊 Бизнес-анализ",
    "BA": "Следующий шаг -> 🧠 Системный анализ",
    "SA": "✅ Закончить",
}

NEXT_STATUS_LIST = ["GRAPH", "BA", "SA"]

RESPONSE_STATUS = {
    "DESC": "Описание успешно сгенерировано",
    "GRAPH": "Граф связей построен",
    "BA": "Бизнес-требования сгенерированы",
    "SA": "Системные требования сгенерированы"
}