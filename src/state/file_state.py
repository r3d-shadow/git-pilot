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

    def cleanup_old(self, repo: str, current_keys):
        """
        Remove state entries whose keys are not in current_keys.
        Returns list of file paths to delete from the remote.
        """
        removed_paths = []
        repo_state = self.state.get("repos", {}).get(repo, {})
        files = repo_state.get("files", {})

        old_keys = set(files.keys())
        to_remove = old_keys - set(current_keys)

        for key in to_remove:
            old_path = files[key].get("file_path")
            if old_path:
                removed_paths.append(old_path)
            del files[key]

        # If no files left, remove entire repo entry
        if not files:
            self.state["repos"].pop(repo, None)
        else:
            self.state["repos"][repo]["files"] = files

        return removed_paths

    def _now_iso(self):
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
