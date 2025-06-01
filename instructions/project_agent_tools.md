# Правила реализации инструментов для агентов

## Пример создания класса инструмента
```python
class RagTool:
    def __init__(self):
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
        example_docs = [
            "Погода в МСК пасмурная",
            "Слон купил велосипед",
            "Bombini Gussini la brateelo Bombordiro Crocodilo"
        ]
        embedding = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        docs = [Document(page_content=text) for text in example_docs]
        vectorstore = FAISS.from_documents(docs, embedding)
        retriver = vectorstore.as_retriever()

        self.rag_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True
        )
    def run_tool(self, query):
        _query = {"query": query}
        result = self.rag_chain.invoke(_query)["result"]
        return result
```

## Пример создания инструмента
```python
rag_chain = RagTool()
class RagResult(BaseModel):
    status: str = Field(description="Статус исполнения RAG")
    message: str = Field(description="Сообщение о результате исполнения RAG")
    result: str = Field(description="Результат исполнения RAG")

few_shot_examples_rag = [
    {
        "request": "Сколько лет Льву Николаевичу Толстому?",
        "params": {"query": "Сколько лет Льву Николаевичу Толстому?"},
    }
]

@giga_tool(few_shot_examples=few_shot_examples_rag)
def rag_search(
    query: str = Field(description="Запрос в векторную БД для RAG")
) -> RagResult:
    """Использование поиска"""
    print(f"! rag_search with query: {query}")
    try:
        result = rag_chain.run_tool(query)
        return RagResult(status="OK", message="Ответ получен!", result=result)
    except Exception as e:
        return RagResult(status="FAIL", message=f"Не удалось запустить инструмент, ошибка: {e}", result=None)
```
