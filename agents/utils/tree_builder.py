from collections import defaultdict
from typing import List


class Tree:
    @staticmethod
    def build_tree(paths: List[str]) -> defaultdict[str, str]:
        tree = lambda: defaultdict(tree)
        root = tree()
        for path in paths:
            parts = path.split("/")
            current = root
            for part in parts:
                current = current[part]
        return root

    @staticmethod
    def tree_to_string(d, prefix=""):
        lines = []
        entries = sorted(d.items())
        for i, (key, subtree) in enumerate(entries):
            connector = "└── " if i == len(entries) - 1 else "├── "
            lines.append(prefix + connector + key)
            extension = "    " if i == len(entries) - 1 else "│   "
            lines.extend(Tree.tree_to_string(subtree, prefix + extension))
        return lines

    @staticmethod
    def create(files: List[str]) -> str:
        tree = Tree.build_tree(files)
        tree_lines = Tree.tree_to_string(tree)
        tree_str = "\n".join(tree_lines)
        return tree_str

