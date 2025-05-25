import os
from collections import ChainMap
import re
from src.core.interfaces import ProviderInterface, StateInterface, TemplateInterface, DiffViewerInterface

class SyncEngine:
    def __init__(self, provider: ProviderInterface, state_mgr: StateInterface, template_eng: TemplateInterface, diff_viewer: DiffViewerInterface):
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
                print(f"No templates for {repo_cfg.name}")
                continue

            synced_keys = []
            for tmpl in selected:
                content = self.template_eng.render(tmpl, merged_vars)
                path = os.path.join(repo_cfg.path, tmpl.rsplit('.', 1)[0])  # Fix here!
                key = tmpl

                diffs = self.provider.sync(
                    repo_cfg.name, repo_cfg.branch, path,
                    content, repo_cfg.message or defaults.get('message', ''),
                    True, self.state_mgr, key
                )
                all_diffs.extend(diffs)
                for d in diffs:
                    plan.append(dict(
                        repo=repo_cfg.name,
                        branch=repo_cfg.branch,
                        path=path,
                        content=content,
                        message=repo_cfg.message,
                        key=key,
                        op=d[1]
                    ))
                synced_keys.append(key)

            old = self.state_mgr.cleanup_old(repo_cfg.name, synced_keys)
            for p in old:
                all_diffs.append((repo_cfg.name, 'delete', p, None, None))
                plan.append(dict(repo=repo_cfg.name, branch=repo_cfg.branch,
                                 path=p, content=None, message=f"remove {p}",
                                 key=None, op='delete'))

        if not all_diffs:
            print("Nothing to do.")
            return

        if not self.diff_viewer.show(all_diffs):
            print("Aborted.")
            return

        for item in plan:
            self.provider.sync(
                item['repo'], item['branch'], item['path'],
                item['content'], item['message'], False,
                self.state_mgr, item['key']
            )
        self.state_mgr.save()
        print("Sync complete.")
