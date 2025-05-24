# cli.py
import argparse
import yaml
import re
import os
from collections import ChainMap
from providers import github
from core import loader
from core.state import StateManager

def main():
    parser = argparse.ArgumentParser(description="Sync multiple templated workflows across GitHub repos")
    parser.add_argument('--provider', choices=['github'], default='github', help='CI provider')
    parser.add_argument('--token', required=True, help='Access token')
    parser.add_argument('--template-dir', required=True, help='Directory containing Jinja2 workflow templates')
    parser.add_argument('--values', required=True, help='Path to values.yaml with repo-specific config')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without committing')
    parser.add_argument('--state-file', default='.ci-sync.json', help='Path to local state file')

    args = parser.parse_args()
    config = yaml.safe_load(open(args.values))
    defaults = config.get('defaults', {})

    all_templates = [f for f in os.listdir(args.template_dir) if os.path.isfile(os.path.join(args.template_dir, f))]
    state_manager = StateManager(path=args.state_file)

    for repo_cfg in config.get('repos', []):
        name = repo_cfg['name']
        branch = repo_cfg.get('branch', defaults.get('branch', 'main'))
        message = repo_cfg.get('message', defaults.get('message', 'ci-sync: update CI workflow'))
        base_path = repo_cfg.get('path', defaults.get('path', '.github/workflows'))

        repo_vars = repo_cfg.get('vars', {})
        default_vars = defaults.get('vars', {})
        merged_vars = dict(ChainMap(repo_vars, default_vars))

        patterns = repo_cfg.get('templates', defaults.get('templates', []))
        selected = []
        for tmpl in all_templates:
            for pat in patterns:
                if re.fullmatch(pat, tmpl):
                    selected.append(tmpl)
                    break

        if not selected:
            print(f"Warning: No templates matched for repo {name}")
            continue

        synced_keys = []
        for tmpl in selected:
            template_path = os.path.join(args.template_dir, tmpl)
            content = loader.load_template(template_path, merged_vars)

            filename = os.path.splitext(tmpl)[0] + '.yml'
            target_path = os.path.join(base_path, filename)
            template_key = tmpl

            if args.provider == 'github':
                github.sync(
                    token=args.token,
                    repos=[name],
                    branch=branch,
                    template_content=content,
                    target_path=target_path,
                    commit_message=message,
                    dry_run=args.dry_run,
                    state_manager=state_manager,
                    template_key=template_key
                )
                synced_keys.append(template_key)

        removed_paths = state_manager.cleanup_old_templates(name, synced_keys)

        for path in removed_paths:
            if args.dry_run:
                print(f"  - Dry run: would remove obsolete file {path}")
            else:
                try:
                    repo = github.Github(args.token).get_repo(name)
                    old_content = repo.get_contents(path, ref=branch)
                    repo.delete_file(path, f"ci-sync: remove obsolete file {path}", old_content.sha, branch=branch)
                    print(f"  - Removed obsolete file {path}")
                except Exception as e:
                    print(f"  - Warning: Failed to delete obsolete file {path}: {e}")

    if not args.dry_run:
        state_manager.save()

if __name__ == '__main__':
    main()
