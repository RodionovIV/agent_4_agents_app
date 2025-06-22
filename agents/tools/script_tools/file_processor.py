import json


class FileProcessor:
    @staticmethod
    def save_str(filename, content):
        with open(filename, mode="w") as f:
            f.write(content)

    @staticmethod
    def read_file(filename):
        with open(filename, "r") as f:
            return f.read()

    @staticmethod
    def read_json(filename):
        with open(filename, "r") as f:
            return json.load(f)
