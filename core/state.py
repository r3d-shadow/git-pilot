import json
import os
import time

class StateManager:
    def __init__(self, path):
        self.path = path
        self.state = self._load_state()

    def _load_state(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                return json.load(f)
        else:
            return {"repos": {}}

    def save(self):
        # Simple atomic save
        tmp_path = self.path + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(self.state, f, indent=2)
        os.replace(tmp_path, self.path)

    def get_repo_state(self, repo_fullname):
        return self.state["repos"].get(repo_fullname, {})

    def update_repo_state(self, repo_fullname, file_path, sha):
        self.state["repos"][repo_fullname] = {
            "file_path": file_path,
            "sha": sha,
            "last_synced": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

    def remove_repo_state(self, repo_fullname):
        if repo_fullname in self.state["repos"]:
            del self.state["repos"][repo_fullname]
