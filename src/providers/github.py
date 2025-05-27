from typing import Any, List, Tuple, Optional
from github import Github
from src.core.interfaces import ProviderInterface
from src.core.comparator import is_same
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
        dry_run: bool,
    ) -> Tuple[List[Tuple[str, str, str, Any, Any]], Optional[str]]:
        """
        Returns:
            - List of diffs (repo, action, path, old, new)
            - SHA of the committed file (if not dry-run and create/update)
        """
        diffs = []
        sha = None
        repository = self.client.get_repo(repo)
        Logger.get_logger().debug(f"Processing {repo} on branch {branch}...")

        try:
            contents = repository.get_contents(path, ref=branch)
            existing = contents.decoded_content.decode()
            sha = contents.sha
        except Exception:
            existing = None

        if is_same(existing, content):
            Logger.get_logger().info(f"  - {repo}:{branch} [{path}] Skipped: already up to date")
            return diffs, sha

        action = "update" if existing else "create"
        if dry_run:
            Logger.get_logger().debug(f"  - Dry run: would {action} {path}")
            diffs.append((repo, action, path, existing, content))
        else:
            if sha:
                res = repository.update_file(path, commit_message, content, sha, branch=branch)
                sha = res["content"].sha
                Logger.get_logger().info(f"  - Updated {path}")
            else:
                res = repository.create_file(path, commit_message, content, branch=branch)
                sha = res["content"].sha
                Logger.get_logger().info(f"  - Created {path}")

        return diffs, sha

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
