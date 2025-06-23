from typing import List, TypedDict


class CoAgentState(TypedDict):
    task: str
    config_task: str
    git_task: str
    config_result: str
    git_result: str
    messages: List
    repo_name: str
