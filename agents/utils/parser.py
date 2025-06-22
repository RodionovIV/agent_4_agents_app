import re


class Parser:
    @staticmethod
    def parse_question(msg: str):
        matches = re.findall(r"\[ВОПРОС\](.*?)\[/ВОПРОС\]", msg, re.DOTALL)
        return matches

    @staticmethod
    def parse_mermaid(result):
        matches = re.search(r"```mermaid(.*?)```", result, re.DOTALL)
        if matches:
            return matches.group(1)
        else:
            return None
