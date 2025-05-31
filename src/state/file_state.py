import json
import os
import time
from typing import List, Tuple, Set
from src.core.interfaces import StateInterface

class FileStateManager(StateInterface):
    def __init__(self, path: str):
        self.path = path
        self.state = {"repos": {}}

    def load(self) -> None:
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {"repos": {}}

    def save(self) -> None:
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.state, f, indent=2)
        os.replace(tmp, self.path)

    def _get_branch_files(self, repo: str, branch: str, provider_name: str) -> dict:
        return self.state.get("repos", {}).get(provider_name, {}).get(repo, {}).get("branches", {}).get(branch, {}).get("files", {})

    def get_file_entry(self, repo: str, branch: str, key: str, provider_name: str) -> dict:
        return self._get_branch_files(repo, branch, provider_name).get(key, {})

    def cleanup_old(self, repo: str, branch: str, current_keys: List[str], provider_name: str) -> List[str]:
        removed_files = []
        branch_files = self._get_branch_files(repo, branch, provider_name)
        if not branch_files:
            return removed_files

        old_keys = set(branch_files.keys())
        to_remove = old_keys - set(current_keys)

        for key in to_remove:
            file_entry = branch_files[key]
            path = file_entry.get("path")
            if path:
                removed_files.append(path)
            del branch_files[key]

        # Clean up empty structures
        provider_repos = self.state["repos"].get(provider_name, {})
        repo_entry = provider_repos.get(repo, {})
        branches = repo_entry.get("branches", {})

        if not branch_files:
            branches.pop(branch, None)
            if not branches:
                provider_repos.pop(repo, None)
                if not provider_repos:
                    self.state["repos"].pop(provider_name, None)

        return removed_files

    def cleanup_old_branches(self, repo: str, active_branches: Set[str], provider_name: str) -> List[Tuple[str, str]]:
        removed_files = []
        repo_branches = self.state.get("repos", {}).get(provider_name, {}).get(repo, {}).get("branches", {})
        if not repo_branches:
            return removed_files

        branches_to_remove = set(repo_branches.keys()) - active_branches

        for branch in branches_to_remove:
            branch_files = repo_branches.get(branch, {}).get("files", {})
            for file_entry in branch_files.values():
                path = file_entry.get("path")
                if path:
                    removed_files.append((branch, path))
            repo_branches.pop(branch, None)

        provider_repos = self.state["repos"].get(provider_name, {})
        if not repo_branches:
            provider_repos.pop(repo, None)
            if not provider_repos:
                self.state["repos"].pop(provider_name, None)

        return removed_files

    def update_file_entry(self, repo: str, branch: str, key: str, file_path: str, sha: str, rendered: str, provider_name: str) -> None:
        self.state.setdefault("repos", {}) \
            .setdefault(provider_name, {}) \
            .setdefault(repo, {}) \
            .setdefault("branches", {}) \
            .setdefault(branch, {}) \
            .setdefault("files", {})[key] = {
                "path": file_path,
                "sha": sha,
                "rendered": rendered,
                "updated_at": self._now_iso()
            }

    @staticmethod
    def _now_iso() -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())