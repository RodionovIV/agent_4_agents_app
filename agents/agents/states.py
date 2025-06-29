from typing import List, TypedDict


class DescAgentState(TypedDict):
    task: str
    messages: List
    questions: str
    result: str


class GraphAgentState(TypedDict):
    task: str
    description: str
    messages: List
    result: str
    questions: List


class BaAgentState(TypedDict):
    task: str
    messages: List
    result: str
    questions: List


class SaAgentState(TypedDict):
    task: str
    description: str
    ba_requirements: str
    messages: List
    result: str
    questions: List


class PlAgentState(TypedDict):
    task: str
    result: str
    messages: List


class CoAgentState(TypedDict):
    task: str
    desc: str
    config_task: str
    git_task: str
    config_result: str
    git_result: str
    messages: List
    repo_name: str
