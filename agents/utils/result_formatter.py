from typing import Dict, TypedDict

from agents.utils.parser import Parser


class ResultFormatter:
    @staticmethod
    def get_result(state: TypedDict) -> Dict[str, str]:
        if "result" in state and state["result"]:
            return {"status": "OK", "content": state["result"]}
        elif "questions" in state and state["questions"]:
            return {"status": "QUES", "content": state["questions"]}
        else:
            return {"status": "FAIL", "content": "Возникла ошибка"}

    @staticmethod
    def get_result_mermaid(state: TypedDict) -> Dict[str, str]:
        if "result" in state and state["result"]:
            return {
                "status": "OK",
                "content": state["result"],
                "mermaid": Parser.parse_mermaid(state["result"]),
            }
        elif "questions" in state and state["questions"]:
            return {"status": "QUES", "content": state["questions"]}
        else:
            return {"status": "FAIL", "content": "Возникла ошибка"}
