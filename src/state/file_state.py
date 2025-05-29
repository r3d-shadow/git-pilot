import json
import os
import time
from src.core.interfaces import StateInterface

class FileStateManager(StateInterface):
    def __init__(self, path: str):
        self.path = path
        self.state = {}

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {"repos": {}}

    def save(self):
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.state, f, indent=2)
        os.replace(tmp, self.path)

    def cleanup_old(self, repo: str, branch: str, current_keys):
        removed_files = []

        branch_files = self.state \
            .get("repos", {}) \
            .get(repo, {}) \
            .get("branches", {}) \
            .get(branch, {}) \
            .get("files", {})

        old_keys = set(branch_files.keys())
        to_remove = old_keys - set(current_keys)

        for key in to_remove:
            file_entry = branch_files[key]
            path = file_entry.get("path")
            if path:
                removed_files.append(path)
            del branch_files[key]

        # Clean up empty structures
        if not branch_files:
            self.state["repos"][repo]["branches"].pop(branch, None)
        if not self.state["repos"][repo]["branches"]:
            self.state["repos"].pop(repo, None)

        return removed_files

    def cleanup_old_branches(self, repo: str, active_branches: set):
        """
        Remove branches from the state that are no longer active.
        Return list of tuples: (branch_name, file_path) for deletion.
        """
        removed_files = []
        repo_branches = self.state.get("repos", {}).get(repo, {}).get("branches", {})

        if not repo_branches:
            return removed_files

        branches_to_remove = set(repo_branches.keys()) - active_branches

        for branch in branches_to_remove:
            branch_files = repo_branches.get(branch, {}).get("files", {})
            for key, file_entry in branch_files.items():
                path = file_entry.get("path")
                if path:
                    removed_files.append((branch, path))
            # Remove the entire branch
            repo_branches.pop(branch, None)

        # If no branches left, remove the repo
        if not repo_branches:
            self.state["repos"].pop(repo, None)

        return removed_files

    def update_file_entry(self, repo: str, branch: str, key: str, file_path: str, sha: str, rendered: str):
        self.state.setdefault("repos", {}) \
            .setdefault(repo, {}) \
            .setdefault("branches", {}) \
            .setdefault(branch, {}) \
            .setdefault("files", {})[key] = {
                "path": file_path,
                "sha": sha,
                "rendered": rendered,
                "updated_at": self._now_iso()
            }

    def _now_iso(self):
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
