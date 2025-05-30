from typing import Any, List, Tuple, Optional
from github import Github
from src.core.interfaces import ProviderInterface
from src.utils.logger import Logger


class GitHubProvider(ProviderInterface):
    def __init__(self, token: str):
        self.client = Github(token)

    def sync(
        self,
        repo: str,
        branch: str,
        path: str,
        content: str,
        commit_message: str,
    ) -> Tuple[List[Tuple[str, str, str, Any, Any]], Optional[str]]:
        """
        Uploads a file to GitHub and returns:
            - SHA of the committed file
        """
        sha = None
        repository = self.client.get_repo(repo)
        Logger.get_logger().debug(f"Processing {repo} on branch {branch}...")

        try:
            contents = repository.get_contents(path, ref=branch)
            sha = contents.sha
            res = repository.update_file(path, commit_message, content, sha, branch=branch)
            sha = res["content"].sha
            Logger.get_logger().debug(f"  - Updated {path}")
        except Exception:
            res = repository.create_file(path, commit_message, content, branch=branch)
            sha = res["content"].sha
            Logger.get_logger().debug(f"  - Created {path}")

        return sha

    def delete(
        self,
        repo: str,
        branch: str,
        path: str,
        commit_message: str
    ) -> None:
        """
        Deletes a file at `path` in `repo` on `branch`.
        """
        repository = self.client.get_repo(repo)
        try:
            contents = repository.get_contents(path, ref=branch)
            repository.delete_file(path, commit_message, contents.sha, branch=branch)
            Logger.get_logger().info(f"  - Deleted file {path}")
        except Exception as e:
            Logger.get_logger().error(f"  - Warning: failed to delete {path}: {e}")