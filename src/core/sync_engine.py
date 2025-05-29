import os
import re
from collections import ChainMap
from typing import Dict, Any
from src.core.interfaces import ProviderInterface, StateInterface, TemplateInterface, DiffViewerInterface
from src.utils.logger import Logger
from src.utils.hash import compute_sha
import time
import json


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

    def sync(self, config):
        defaults = config.defaults
        all_diffs = []
        plan = []

        for repo_cfg in config.repos:
            merged_vars = dict(ChainMap(repo_cfg.vars, defaults.get('vars', {})))

            patterns = repo_cfg.templates or defaults.get('templates', [])
            templates = self.template_eng.list_templates(self.template_eng.root_dir)
            selected = [t for t in templates if any(re.fullmatch(p, t) for p in patterns)]

            if not selected:
                Logger.get_logger().warning(f"No templates matched for {repo_cfg.name}")
                continue

            branch = getattr(repo_cfg, 'branch', None)
            message = getattr(repo_cfg, 'message', None)
            path_root = getattr(repo_cfg, 'path', None)

            if not branch or not message or not path_root:
                Logger.get_logger().error(f"Missing required fields in config for repo '{repo_cfg.name}'")
                raise ValueError(f"Missing required fields in config for repo '{repo_cfg.name}'")

            synced_keys = []

            for tmpl in selected:
                content = self.template_eng.render(tmpl, merged_vars)
                target_path = os.path.join(path_root, tmpl.rsplit('.', 1)[0])
                key = tmpl
                current_sha = compute_sha(content)

                existing_entry = self.state_mgr.state.get("repos", {}) \
                    .get(repo_cfg.name, {}) \
                    .get("branches", {}) \
                    .get(branch, {}) \
                    .get("files", {}) \
                    .get(key, {})

                previous_sha = existing_entry.get("sha")
                previous_content = existing_entry.get("rendered")

                synced_keys.append(key)

                if current_sha == previous_sha:
                    Logger.get_logger().info(f"{repo_cfg.name}:{branch} [{target_path}] Skipped (unchanged)")
                    continue

                action = "update" if previous_sha else "create"
                diffs = [(repo_cfg.name, branch, action, target_path, previous_content, content)]
                all_diffs.extend(diffs)

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

            # ALSO cleanup old branches that are no longer active in config for this repo
            active_branches = {getattr(r, 'branch', None) for r in config.repos if r.name == repo_cfg.name}
            # Remove None values just in case
            active_branches.discard(None)

            old_branch_files = self.state_mgr.cleanup_old_branches(repo_cfg.name, active_branches)
            for branch, path in old_branch_files:
                all_diffs.append((repo_cfg.name, branch, 'delete', path, None, None))
                plan.append(dict(
                    repo=repo_cfg.name,
                    branch=branch,
                    path=path,
                    content=None,
                    message=f"remove {path} from old branch {branch}",
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
