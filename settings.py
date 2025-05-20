from langchain_gigachat.chat_models import GigaChat

import os

os.environ["GIGACHAT_CREDENTIALS"] = "Yjc1YWZhNTItMzYwYS00NmU4LTk4YjctZjU4YzAwMDIyMGJmOjJhNWE3YmVhLTAyYzctNGJhNy05NWE3LWEzY2YwNGQzYzZiNw=="

with open("instructions/ba_instruction.md", "r") as f:
    ba_instruction = f.read()

with open("prompts/ba_prompt.txt", "r") as f:
    ba_prompt = f.read()

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