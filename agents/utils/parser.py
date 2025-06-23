import json
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

    @staticmethod
    def parse_json(text: str):
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        result = text
        if match:
            result_str = match.group(1)
            result = json.loads(result_str)
        return result
