from typing import TypedDict, Dict


class ParseResult:
    @staticmethod
    def get_result(state: TypedDict) -> Dict[str, str]:
        if "result" in state and state["result"]:
            return {"status": "OK", "content": state["result"]}
        elif "questions" in state and state["questions"]:
            return {"status": "QUES", "content": state["questions"]}
        else:
            return {"status": "FAIL", "content": "Возникла ошибка"}
