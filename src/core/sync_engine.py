import os
import re
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
        diff_viewer: DiffViewerInterface,
        interactive: bool = True,
        provider_name: str = None
    ):
        self.provider = provider
        self.state_mgr = state_mgr
        self.template_eng = template_eng
        self.diff_viewer = diff_viewer
        self.interactive = interactive  
        self.provider_name = provider_name  

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

                existing_entry = self.state_mgr.get_file_entry(repo_cfg.name, branch, key, self.provider_name)
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

            self._handle_old_files(repo_cfg, synced_keys, all_diffs, plan, config)

        if not all_diffs:
            Logger.get_logger().info("Nothing to do.")
            return

        if self.interactive:
            if not self.diff_viewer.show(all_diffs):
                Logger.get_logger().info("Aborted.")
                return
        else:
            Logger.get_logger().info("Non-interactive mode: Skipping diff viewer.")

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

                Logger.get_logger().info(
                    f"{item['repo']} ({item['branch']})/{item['path']} [{item['op']}]"
                )

                if item["key"]:
                    self.state_mgr.update_file_entry(
                        repo=item["repo"],
                        branch=item["branch"],
                        key=item["key"],
                        file_path=item["path"],
                        sha=item["sha"],
                        rendered=item["content"],
                        provider_name=self.provider_name,
                    )

        self.state_mgr.save()
        Logger.get_logger().info("Sync complete.")

    def _handle_old_files(self, repo_cfg, synced_keys, all_diffs, plan, config):
        old_files = self.state_mgr.cleanup_old(repo_cfg.name, repo_cfg.branch, synced_keys, self.provider_name)
        for p in old_files:
            all_diffs.append((repo_cfg.name, repo_cfg.branch, 'delete', p, None, None))
            plan.append(dict(
                repo=repo_cfg.name,
                branch=repo_cfg.branch,
                path=p,
                content=None,
                message=f"remove {p}",
                key=None,
                op='delete'
            ))

        active_branches = {r.branch for r in config.repos if r.name == repo_cfg.name}
        old_branch_files = self.state_mgr.cleanup_old_branches(repo_cfg.name, active_branches, self.provider_name)
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