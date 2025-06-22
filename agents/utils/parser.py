import re


class Parser:
    @staticmethod
    def parse_question(msg:str):
        matches = re.findall(r"\[ВОПРОС\](.*?)\[/ВОПРОС\]", msg, re.DOTALL)
        return matches
