import argparse
from providers import github
from core import loader, comparator

def main():
    parser = argparse.ArgumentParser(description="Sync CI workflows across GitHub repos")
    parser.add_argument('--provider', choices=['github'], default='github', help='CI provider')
    parser.add_argument('--token', required=True, help='Access token')
    parser.add_argument('--repos', required=True, help='Comma-separated list of GitHub repositories (owner/repo)')
    parser.add_argument('--branch', default='main', help='Target branch')
    parser.add_argument('--template', required=True, help='Path to local workflow template')
    parser.add_argument('--path', default='.github/workflows/ci.yml', help='Target file path in repo')
    parser.add_argument('--message', default='ci-sync: update CI workflow', help='Commit message for workflow update')

    args = parser.parse_args()
    repo_list = [r.strip() for r in args.repos.split(',') if r.strip()]
    template_content = loader.load_template(args.template)

    if args.provider == 'github':
        github.sync(
            token=args.token,
            repos=repo_list,
            branch=args.branch,
            template_content=template_content,
            target_path=args.path,
            commit_message=args.message
        )

if __name__ == '__main__':
    main()