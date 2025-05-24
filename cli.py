import argparse
import yaml
from providers import github
from core import loader, comparator
from collections import ChainMap

def main():
    parser = argparse.ArgumentParser(description="Sync CI workflows across GitHub repos")
    parser.add_argument('--provider', choices=['github'], default='github', help='CI provider')
    parser.add_argument('--token', required=True, help='Access token')
    parser.add_argument('--template', required=True, help='Path to local workflow template (Jinja2 supported)')
    parser.add_argument('--values', required=True, help='Path to values.yaml with repo-specific config')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without committing')

    args = parser.parse_args()

    with open(args.values) as f:
        config = yaml.safe_load(f)

    defaults = config.get("defaults", {})

    for repo in config.get("repos", []):
        name = repo["name"]
        branch = repo.get("branch", defaults.get("branch", "main"))
        message = repo.get("message", defaults.get("message", "ci-sync: update CI workflow"))
        path = repo.get("path", defaults.get("path", ".github/workflows/ci.yml"))

        # 🧠 Merge default + repo vars
        repo_vars = repo.get("vars", {})
        default_vars = defaults.get("vars", {})
        merged_vars = dict(ChainMap(repo_vars, default_vars))

        template_content = loader.load_template(args.template, merged_vars)

        if args.provider == "github":
            github.sync(
                token=args.token,
                repos=[name],
                branch=branch,
                template_content=template_content,
                target_path=path,
                commit_message=message,
                dry_run=args.dry_run
            )

if __name__ == '__main__':
    main()
