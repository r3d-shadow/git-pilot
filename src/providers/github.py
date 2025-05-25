from typing import Any, List, Tuple, Optional
from github import Github
from src.core.interfaces import ProviderInterface
from src.core.comparator import is_same

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
        state_manager,
        template_key: Optional[str] = None
    ) -> List[Tuple[str, str, str, Any, Any]]:
        """
        Dry-run: returns list of diffs (repo, action, path, old, new).
        Real run: creates/updates file and updates state_manager.
        """
        diffs: List[Tuple[str, str, str, Any, Any]] = []
        repository = self.client.get_repo(repo)
        print(f"Processing {repo} on branch {branch}...")

        # 1. Delete old path if moved
        prev_files = (
            state_manager.state.get("repos", {})
            .get(repo, {})
            .get("files", {})
        )
        if template_key and template_key in prev_files:
            old_path = prev_files[template_key]["file_path"]
            if old_path and old_path != path:
                if dry_run:
                    print(f"  - Dry run: would delete old file {old_path}")
                    diffs.append((repo, "delete", old_path, None, None))
                else:
                    try:
                        old_obj = repository.get_contents(old_path, ref=branch)
                        repository.delete_file(
                            old_path,
                            f"ci-sync: remove old workflow file {old_path}",
                            old_obj.sha,
                            branch=branch
                        )
                        print(f"  - Deleted old file {old_path}")
                    except Exception as e:
                        print(f"  - Warning: could not delete {old_path}: {e}")

        # 2. Fetch existing file
        try:
            contents = repository.get_contents(path, ref=branch)
            existing = contents.decoded_content.decode()
            sha = contents.sha
        except Exception:
            existing = None
            sha = None

        # 3. If identical, skip
        if is_same(existing, content):
            print("  - Skipped: already up to date")
            return diffs

        action = "update" if existing else "create"
        if dry_run:
            print(f"  - Dry run: would {action} {path}")
            diffs.append((repo, action, path, existing, content))
        else:
            if sha:
                repository.update_file(path, commit_message, content, sha, branch=branch)
                print(f"  - Updated {path}")
            else:
                repository.create_file(path, commit_message, content, branch=branch)
                print(f"  - Created {path}")

            # Update state
            if state_manager and template_key:
                state_manager.state \
                    .setdefault("repos", {}) \
                    .setdefault(repo, {}) \
                    .setdefault("files", {})[template_key] = {
                        "file_path": path,
                        "sha": sha or "new",
                        "last_synced": state_manager._now_iso()
                    }

        return diffs

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
            print(f"  - Deleted file {path}")
        except Exception as e:
            print(f"  - Warning: failed to delete {path}: {e}")
