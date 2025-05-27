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

    def cleanup_old(self, repo: str, current_keys, current_branch: str):
        """
        Remove state entries whose keys are not in current_keys
        or whose branch does not match the current branch.

        Returns list of (file_path, branch) tuples to delete from the remote.
        """
        removed_files = []
        repo_state = self.state.get("repos", {}).get(repo, {})
        files = repo_state.get("files", {})

        old_keys = set(files.keys())
        to_remove = set()

        for key in old_keys:
            file_entry = files[key]
            # Mark for removal if key not in current keys or branch changed
            if key not in current_keys or file_entry.get("branch") != current_branch:
                old_path = file_entry.get("file_path")
                old_branch = file_entry.get("branch")
                if old_path and old_branch:
                    removed_files.append((old_path, old_branch))
                to_remove.add(key)

        for key in to_remove:
            del files[key]

        if not files:
            self.state["repos"].pop(repo, None)
        else:
            self.state["repos"][repo]["files"] = files

        return removed_files

    def _now_iso(self):
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
