import os
import re
from collections import ChainMap
from typing import Any
from src.core.interfaces import ProviderInterface, StateInterface, TemplateInterface, DiffViewerInterface
from src.utils.logger import Logger
from src.utils.hash import compute_sha


class SyncEngine:
    def __init__(
        self,
        provider: ProviderInterface,
        state_mgr: StateInterface,
        template_eng: TemplateInterface,
        diff_viewer: DiffViewerInterface
    ):
        self.provider = provider
        self.state_mgr = state_mgr
        self.template_eng = template_eng
        self.diff_viewer = diff_viewer

    def sync(self, config: Any) -> None:
        all_diffs = []
        plan = []

        for repo_cfg in config.repos:
            merged_vars = repo_cfg.vars or {}
            patterns = repo_cfg.templates or []
            templates = self.template_eng.list_templates(self.template_eng.root_dir)
            selected = [t for t in templates if any(re.fullmatch(p, t) for p in patterns)]

            if not selected:
                Logger.get_logger().warning(f"No templates matched for {repo_cfg.name}")
                continue

            branch = repo_cfg.branch
            message = repo_cfg.message
            path_root = repo_cfg.path

            if not (branch and message and path_root):
                Logger.get_logger().error(f"Missing required fields in config for repo '{repo_cfg.name}'")
                raise ValueError(f"Missing required fields in config for repo '{repo_cfg.name}'")

            synced_keys = []

            for tmpl in selected:
                content = self.template_eng.render(tmpl, merged_vars)
                target_path = os.path.join(path_root, tmpl.rsplit('.', 1)[0])
                key = tmpl
                current_sha = compute_sha(content)

                existing_entry = self._get_existing_entry(repo_cfg.name, branch, key)
                previous_sha = existing_entry.get("sha")
                previous_content = existing_entry.get("rendered")

                synced_keys.append(key)

                if current_sha == previous_sha:
                    Logger.get_logger().info(f"{repo_cfg.name}:{branch} [{target_path}] Skipped (unchanged)")
                    continue

                action = "update" if previous_sha else "create"
                all_diffs.append((repo_cfg.name, branch, action, target_path, previous_content, content))

                plan.append(dict(
                    repo=repo_cfg.name,
                    branch=branch,
                    path=target_path,
                    content=content,
                    message=message,
                    key=key,
                    op=action,
                    sha=current_sha
                ))

            # Cleanup old files for current branch
            old_files = self.state_mgr.cleanup_old(repo_cfg.name, branch, synced_keys)
            for p in old_files:
                all_diffs.append((repo_cfg.name, branch, 'delete', p, None, None))
                plan.append(dict(
                    repo=repo_cfg.name,
                    branch=branch,
                    path=p,
                    content=None,
                    message=f"remove {p}",
                    key=None,
                    op='delete'
                ))

            # Cleanup old branches no longer active for this repo
            active_branches = {r.branch for r in config.repos if r.name == repo_cfg.name}
            old_branch_files = self.state_mgr.cleanup_old_branches(repo_cfg.name, active_branches)
            for branch_name, path in old_branch_files:
                all_diffs.append((repo_cfg.name, branch_name, 'delete', path, None, None))
                plan.append(dict(
                    repo=repo_cfg.name,
                    branch=branch_name,
                    path=path,
                    content=None,
                    message=f"remove {path} from old branch {branch_name}",
                    key=None,
                    op='delete'
                ))

        if not all_diffs:
            Logger.get_logger().info("Nothing to do.")
            return

        if not self.diff_viewer.show(all_diffs):
            Logger.get_logger().info("Aborted.")
            return

        for item in plan:
            if item["op"] == "delete":
                self.provider.delete(
                    repo=item["repo"],
                    branch=item["branch"],
                    path=item["path"],
                    commit_message=item["message"]
                )
            else:
                sha = self.provider.sync(
                    repo=item["repo"],
                    branch=item["branch"],
                    path=item["path"],
                    content=item["content"],
                    commit_message=item["message"],
                )
                if item["key"]:
                    self.state_mgr.update_file_entry(
                        repo=item["repo"],
                        branch=item["branch"],
                        key=item["key"],
                        file_path=item["path"],
                        sha=item["sha"],
                        rendered=item["content"]
                    )

        self.state_mgr.save()
        Logger.get_logger().info("Sync complete.")

    def _get_existing_entry(self, repo: str, branch: str, key: str) -> dict:
        return self.state_mgr.state.get("repos", {}) \
            .get(repo, {}) \
            .get("branches", {}) \
            .get(branch, {}) \
            .get("files", {}) \
            .get(key, {})