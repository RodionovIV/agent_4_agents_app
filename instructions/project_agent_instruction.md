# Правила реализации агента

## Необходимые импорты
```python
from langchain_gigachat.chat_models import GigaChat
from langchain_gigachat.tools.giga_tool import giga_tool

from langchain.schema import HumanMessage, SystemMessage, Document, AIMessage
from langchain.vectorstores import FAISS
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.chains import RetrievalQA
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Optional, Literal, List, Dict
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

from pathlib import Path
import time
import datetime
import warnings
import os
import re
```

## Создание LLM-клиента для агента
```python
llm = GigaChat(
    model="GigaChat-2-Max",
    verify_ssl_certs=False,
    profanity_check=False,
    streaming=False,
    max_tokens=8192,
    temperature=0.3,
    repetition_penalty=1.01,
    timeout=60
)
```

## Пример создания агента
```python
functions = [rag_search]
llm_with_functions = llm.bind_tools(functions)
agent_executor = create_react_agent(llm_with_functions, 
                                    functions,
                                    checkpointer=MemorySaver()
                                   )
```

## Пример запуска агента
```python
config = {"configurable": {"thread_id": "thread_id4"}}
message = {
    "messages": [HumanMessage(content=msg)]
}
result = agent_executor.invoke(message, config=config)
```