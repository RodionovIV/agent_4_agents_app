import json
from pathlib import Path


class FileProcessor:
    @staticmethod
    def save_str(filename, content):
        file_path = Path(filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open(mode="w") as f:
            f.write(content)

    @staticmethod
    def read_file(filename):
        with open(filename, "r") as f:
            return f.read()

    @staticmethod
    def read_json(filename):
        with open(filename, "r") as f:
            return json.load(f)
