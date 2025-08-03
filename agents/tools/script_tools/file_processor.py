import json
from pathlib import Path
from typing import Dict, Any


class FileProcessor:
    @staticmethod
    def save_str(filename: str, content: str) -> None:
        file_path = Path(filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open(mode="w") as f:
            f.write(content)

    @staticmethod
    def read_file(filename: str) -> str:
        with open(filename, "r") as f:
            return f.read()

    @staticmethod
    def read_json(filename: str) -> Dict[str, Any]:
        with open(filename, "r") as f:
            return json.load(f)
