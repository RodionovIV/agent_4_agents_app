import os
import json
from typing import Dict, Any, Tuple
from aiohttp import ClientSession
from dotenv import load_dotenv

from utils.cutomLogger import customLogger

_LOGGER = customLogger.getLogger(__name__)

load_dotenv()

class VersionControl:
    def __init__(self):
        git_cred = os.getenv("VC_CRED")
        self.headers = {
            "Authorization": f"token {git_cred}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.branch = "main"
        self.base_url = "https://api.github.com/repos/"

    async def put(self, data: Dict[str, Any], url: str = None) -> Dict[str, Any]:
        async with ClientSession(
                base_url=self.base_url,
                headers=self.headers,
                raise_for_status=True) as session:
            async with session.put(url, data=json.dumps(data)) as response:
                response = await response.json()
                return response

    async def post(self, data: Dict[str, Any], url: str = None) -> Dict[str, Any]:
        async with ClientSession(
                base_url=self.base_url,
                headers=self.headers,
                raise_for_status=True) as session:
            async with session.post(url, data=json.dumps(data)) as response:
                response = await response.json()
                return response

    async def get(self, url: str = None) -> Dict[str, Any]:
        async with ClientSession(
                base_url=self.base_url,
                headers=self.headers,
                raise_for_status=True) as session:
            async with session.get(url) as response:
                response = await response.json()
                return response

    async def create_repo(self, repo_name: str) -> Dict[str, Any]:
        data = {"name": repo_name}
        async with ClientSession(headers=self.headers, raise_for_status=True) as session:
            async with session.post("https://api.github.com/user/repos", data=json.dumps(data)) as response:
                response = await response.json()
        return response

    async def create_readme(self, repo_name: str) -> None:
        url = f"RodionovIV/{repo_name}/contents/README.md"
        data = {
            "message": "Initial commit via API",
            "content": "SGVsbG8gV29ybGQh",  # base64("Hello World!")
            "branch": self.branch,
        }
        await self.put(data, url=url)

    @staticmethod
    def read_file_content(file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    async def get_latest_commit_info(self, repo_name: str) -> Dict[str, str]:
        ref_url = f"RodionovIV/{repo_name}/git/ref/heads/{self.branch}"
        response = await self.get(url=ref_url)
        commit_sha = response["object"]["sha"]

        commit_url = f"RodionovIV/{repo_name}/git/commits/{commit_sha}"
        response = await self.get(url=commit_url)
        base_tree_sha = response["tree"]["sha"]
        return {"commit_sha": commit_sha, "base_tree_sha": base_tree_sha}

    async def create_blob(self, content: str, repo_name: str) -> str:
        blob_url = f"RodionovIV/{repo_name}/git/blobs"
        data = {"content": content, "encoding": "utf-8"}
        response = await self.post(data, url=blob_url)
        return response["sha"]

    async def create_tree(self,
        base_tree_sha: str,
        repo_name: str,
        files: Dict[str, str]
    ) -> str:

        tree = []
        for file, content in files.items():
            _LOGGER.info(f"Добавляем файл {file}")
            blob_sha = await self.create_blob(content, repo_name)
            tree.append(
                {"path": file, "mode": "100644", "type": "blob", "sha": blob_sha}
            )

        tree_url = f"RodionovIV/{repo_name}/git/trees"
        data = {"base_tree": base_tree_sha, "tree": tree}
        response = await self.post(data, url=tree_url)
        return response["sha"]

    async def create_commit(self,
        tree_sha: str,
        parent_commit_sha: str,
        repo_name: str
    ) -> None:

        commit_url = f"RodionovIV/{repo_name}/git/commits"
        data = {
            "message": "Initial",
            "tree": tree_sha,
            "parents": [parent_commit_sha],
            "author": {"name": "RodionovIV", "email": "mr.ts777@yandex.ru"},
        }
        response = await self.post(data, url=commit_url)
        return response["sha"]

    # === 5. Обновить ветку ===
    async def update_branch_reference(self, new_commit_sha, repo_name):
        ref_url = f"RodionovIV/{repo_name}/git/refs/heads/{self.branch}"
        data = {"sha": new_commit_sha}
        await self.post(data, url=ref_url)
        _LOGGER.info("✅ Файлы успешно загружены и ветка обновлена!")

    async def run(self, repo_name: str, files: Dict[str, str]) -> None:
        _LOGGER.info("Начинаем...")
        await self.create_repo(repo_name)
        _LOGGER.info("Заливаем README...")
        await self.create_readme(repo_name)
        _LOGGER.info("Получаем хэши последнего коммита")
        sha = await self.get_latest_commit_info(repo_name)
        tree_sha = await self.create_tree(sha.get("base_tree_sha"), repo_name, files)
        new_commit_sha = await self.create_commit(tree_sha, sha.get("commit_sha"), repo_name)
        await self.update_branch_reference(new_commit_sha, repo_name)
