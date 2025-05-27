import os
import re
from collections import ChainMap
from typing import Dict, Any
from src.core.interfaces import ProviderInterface, StateInterface, TemplateInterface, DiffViewerInterface
from src.utils.logger import Logger


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
            # Merge variables with defaults
            merged_vars = dict(ChainMap(repo_cfg.vars, defaults.get('vars', {})))

            # Get templates to use by matching patterns
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
                target_path = os.path.join(path_root, tmpl.rsplit('.', 1)[0])  # strip extension
                key = tmpl

                # Dry run: get diffs
                diffs, _ = self.provider.sync(
                    repo=repo_cfg.name,
                    branch=branch,
                    path=target_path,
                    content=content,
                    commit_message=message,
                    dry_run=True
                )

                # Add branch into each diff tuple for uniformity
                all_diffs.extend([
                    (repo_cfg.name, branch, op, path, old, new)
                    for (_, op, path, old, new) in diffs
                ])

                for d in diffs:
                    plan.append(dict(
                        repo=repo_cfg.name,
                        branch=branch,
                        path=target_path,
                        content=content,
                        message=message,
                        key=key,
                        op=d[1]  # 'create' or 'update'
                    ))

                synced_keys.append(key)

            # Cleanup old state and prepare deletions
            # Important: assume cleanup_old returns List[Tuple[file_path, branch]]
            old_files = self.state_mgr.cleanup_old(repo_cfg.name, synced_keys, branch)
            for p, old_branch in old_files:
                all_diffs.append((repo_cfg.name, old_branch, 'delete', p, None, None))
                plan.append(dict(
                    repo=repo_cfg.name,
                    branch=old_branch,
                    path=p,
                    content=None,
                    message=f"remove {p}",
                    key=None,
                    op='delete'
                ))

        if not all_diffs:
            Logger.get_logger().info("Nothing to do.")
            return

        # Show interactive diff and confirm
        if not self.diff_viewer.show(all_diffs):
            Logger.get_logger().info("Aborted.")
            return

        # Apply changes
        for item in plan:
            if item["op"] == "delete":
                self.provider.delete(
                    repo=item["repo"],
                    branch=item["branch"],
                    path=item["path"],
                    commit_message=item["message"]
                )
            else:
                diffs, sha = self.provider.sync(
                    repo=item["repo"],
                    branch=item["branch"],
                    path=item["path"],
                    content=item["content"],
                    commit_message=item["message"],
                    dry_run=False
                )

                if item["key"]:
                    self.state_mgr.state \
                        .setdefault("repos", {}) \
                        .setdefault(item["repo"], {}) \
                        .setdefault("files", {})[item["key"]] = {
                            "file_path": item["path"],
                            "sha": sha or "unknown",
                            "branch": item["branch"],
                            "last_synced": self.state_mgr._now_iso()
                        }

        self.state_mgr.save()
        Logger.get_logger().info("Sync complete.")