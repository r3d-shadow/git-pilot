import argparse
import yaml
import re
import os
from collections import ChainMap
from providers import github
from core import loader
from core.state import StateManager
from core.init import write_example_structure
from core.diff import interactive_diff_view

def init_cmd(args):
    write_example_structure(args.template_dir)
    print(f"Template structure initialized in {args.template_dir}")

def sync_cmd(args):
    config = yaml.safe_load(open(args.values))
    defaults = config.get('defaults', {})

    all_templates = [
        f for f in os.listdir(args.template_dir)
        if os.path.isfile(os.path.join(args.template_dir, f))
    ]
    state_manager = StateManager(path=args.state_file)
    all_diffs = []

    render_plan = []  # Store what to apply if confirmed

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

            filename = os.path.splitext(tmpl)[0]
            target_path = os.path.join(base_path, filename)
            template_key = tmpl

            # Always perform dry-run first
            diffs = github.sync(
                token=args.token,
                repos=[name],
                branch=branch,
                template_content=content,
                target_path=target_path,
                commit_message=message,
                dry_run=True,
                state_manager=state_manager,
                template_key=template_key
            )
            for diff in diffs:
                all_diffs.append(diff)
                render_plan.append({
                    "repo": name,
                    "branch": branch,
                    "message": message,
                    "path": target_path,
                    "content": content,
                    "template_key": template_key,
                    "operation": diff[1]
                })
            synced_keys.append(template_key)

        removed_paths = state_manager.cleanup_old_templates(name, synced_keys)

        for path in removed_paths:
            all_diffs.append((name, 'delete', path, False, None))
            render_plan.append({
                "repo": name,
                "branch": branch,
                "message": f"ci-sync: remove obsolete file {path}",
                "path": path,
                "content": None,
                "template_key": None,
                "operation": "delete"
            })

    if all_diffs:
        confirmed = interactive_diff_view(all_diffs)
        if not confirmed:
            print("Aborting sync. No changes applied.")
            return

        # Apply the stored render plan
        for item in render_plan:
            repo_name = item["repo"]
            branch = item["branch"]
            path = item["path"]
            message = item["message"]
            content = item["content"]
            template_key = item["template_key"]
            operation = item["operation"]

            if operation == "delete":
                try:
                    repo = github.Github(args.token).get_repo(repo_name)
                    old_content = repo.get_contents(path, ref=branch)
                    repo.delete_file(path, message, old_content.sha, branch=branch)
                    print(f"  - Removed obsolete file {path}")
                except Exception as e:
                    print(f"  - Warning: Failed to delete obsolete file {path}: {e}")
            elif operation in ["create", "update"]:
                github.sync(
                    token=args.token,
                    repos=[repo_name],
                    branch=branch,
                    template_content=content,
                    target_path=path,
                    commit_message=message,
                    dry_run=False,
                    state_manager=state_manager,
                    template_key=template_key
                )

        state_manager.save()

def main():
    parser = argparse.ArgumentParser(description="ci-sync: sync reusable CI templates across GitHub repos")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # init command
    init_parser = subparsers.add_parser('init', help='Initialize Jinja2 template scaffold like Helm charts')
    init_parser.add_argument('--template-dir', required=True, help='Directory to bootstrap template structure')
    init_parser.set_defaults(func=init_cmd)

    # sync command
    sync_parser = subparsers.add_parser('sync', help='Sync rendered workflows to GitHub repositories')
    sync_parser.add_argument('--provider', choices=['github'], default='github', help='CI provider')
    sync_parser.add_argument('--token', required=True, help='Access token')
    sync_parser.add_argument('--template-dir', required=True, help='Directory containing Jinja2 workflow templates')
    sync_parser.add_argument('--values', required=True, help='Path to values.yaml with repo-specific config')
    sync_parser.add_argument('--state-file', default='.ci-sync.json', help='Path to local state file')
    sync_parser.set_defaults(func=sync_cmd)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
