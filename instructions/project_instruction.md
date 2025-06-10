# Структура репоризитория
project_name/
├── main.py                # Точка входа в приложение
├── api/
│   └── endpoints.py       # FastAPI роутеры
├── models/
│   ├── agent.py           # Pydantic модели: AgentRequest, AgentResponse
├── services/
│   └── agent_system.py    # Логика агента (AgentSystem класс)
└── dependencies/          # (необязательно) зависимости, например для DI