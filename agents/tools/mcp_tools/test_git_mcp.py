from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
import sys

import subprocess
import os

mcp = FastMCP("Git")

@mcp.tool()
def git_status(repo_path):
    """Use this tool for call git status command for repo_path"""
    print(f"Call git_status for {repo_path}")
    result = subprocess.run(
        ['git', 'status'],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    return result

@mcp.tool()
def git_add(repo_path, file):
    """
    Use this tool for call git add file command for repo_path.
    """
    print(f"Call git_add for {repo_path}")
    result = subprocess.run(
        ['git', 'add', file],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    return result

@mcp.tool()
def git_commit(repo_path, msg):
    """
    Use this tool for call git commit command for repo_path.
    Come up with a small informative message about the changes that will be committed to the repository.
    """
    print(f"Call git_commit for {repo_path}")
    result = subprocess.run(
        ['git', 'commit', "-m", msg],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    return result

@mcp.tool()
def git_branch(repo_path):
    """
    Use this command to get the current branch in the repository.
    """
    print(f"Call git_branch for {repo_path}")
    result = subprocess.run(
        ['git', 'branch'],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    return result

@mcp.tool()
def git_push(repo_path):
    """
    Use this command to for call git push command.
    """
    print(f"Call git_push for {repo_path}")
    result = subprocess.run(
        ['git', 'push'],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    return result

@mcp.tool()
def git_remote_add(repo_path, remote_url, branch_name):
    """
    Use this tool for call git remote add command for repo_path.
    To select a branch, use the git branch command.
    """
    print(f"Call git_remote_add for {repo_path}")
    result = subprocess.run(
        ["git", "remote", "add", "origin", remote_url],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    result = subprocess.run(
        ["git", "branch", "-M", branch_name],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    result = subprocess.run(
        ["git", "push", "-u", "origin", branch_name],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    return result



if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    mcp.run(transport=transport)
    # /media/ts777/Kingston/Sandbox/project_1