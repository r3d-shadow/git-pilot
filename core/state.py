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

    def update_repo_file(self, repo_fullname, template_key, file_path, sha):
        repo_state = self.state["repos"].setdefault(repo_fullname, {})
        files = repo_state.setdefault("files", {})
        files[template_key] = {
            "file_path": file_path,
            "sha": sha,
            "last_synced": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

    def remove_repo_state(self, repo_fullname):
        if repo_fullname in self.state["repos"]:
            del self.state["repos"][repo_fullname]

    def cleanup_old_templates(self, repo_fullname, current_keys):
        """
        Remove template state entries that no longer exist in current sync.
        Returns a list of removed paths (for potential deletion).
        """
        removed_paths = []
        repo_state = self.state["repos"].get(repo_fullname, {})
        files = repo_state.get("files", {})

        old_keys = set(files.keys())
        to_remove = old_keys - set(current_keys)

        for key in to_remove:
            old_path = files[key].get("file_path")
            if old_path:
                removed_paths.append(old_path)
            del files[key]

        if not files:
            self.state["repos"].pop(repo_fullname, None)
        else:
            self.state["repos"][repo_fullname]["files"] = files

        return removed_paths
