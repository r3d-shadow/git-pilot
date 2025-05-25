import os
import re
from collections import ChainMap
from src.core.interfaces import ProviderInterface, StateInterface, TemplateInterface, DiffViewerInterface


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
            # Merge variables
            merged_vars = dict(ChainMap(repo_cfg.vars, defaults.get('vars', {})))

            # Get templates to use
            patterns = repo_cfg.templates or defaults.get('templates', [])
            templates = self.template_eng.list_templates(self.template_eng.root_dir)
            selected = [t for t in templates if any(re.fullmatch(p, t) for p in patterns)]

            if not selected:
                print(f"No templates matched for {repo_cfg.name}")
                continue

            branch = getattr(repo_cfg, 'branch', None)
            message = getattr(repo_cfg, 'message', None)
            path_root = getattr(repo_cfg, 'path', None)

            # Validate required fields
            if not branch or not message or not path_root:
                raise ValueError(f"Missing required fields in config for repo '{repo_cfg.name}'")

            synced_keys = []
            for tmpl in selected:
                # Render template
                content = self.template_eng.render(tmpl, merged_vars)
                target_path = os.path.join(path_root, tmpl.rsplit('.', 1)[0])  # e.g., ".github/workflows/foo"

                key = tmpl
                diffs = self.provider.sync(
                    repo_cfg.name, branch, target_path,
                    content, message, True,
                    self.state_mgr, key
                )

                all_diffs.extend(diffs)
                for d in diffs:
                    plan.append(dict(
                        repo=repo_cfg.name,
                        branch=branch,
                        path=target_path,
                        content=content,
                        message=message,
                        key=key,
                        op=d[1]
                    ))
                synced_keys.append(key)

            # Cleanup old files no longer synced
            old = self.state_mgr.cleanup_old(repo_cfg.name, synced_keys)
            for p in old:
                all_diffs.append((repo_cfg.name, 'delete', p, None, None))
                plan.append(dict(
                    repo=repo_cfg.name,
                    branch=branch,
                    path=p,
                    content=None,
                    message=f"remove {p}",
                    key=None,
                    op='delete'
                ))

        # Exit early if no changes
        if not all_diffs:
            print("Nothing to do.")
            return

        # Interactive diff approval
        if not self.diff_viewer.show(all_diffs):
            print("Aborted.")
            return

        # Apply plan
        for item in plan:
            self.provider.sync(
                item['repo'], item['branch'], item['path'],
                item['content'], item['message'], False,
                self.state_mgr, item['key']
            )

        self.state_mgr.save()
        print("Sync complete.")
