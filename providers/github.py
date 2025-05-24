from core.diff import generate_diff
from github import Github
from core import comparator

def sync(token, repos, branch, template_content, target_path, commit_message, dry_run=False):
    github = Github(token)
    for repo_fullname in repos:
        repo = github.get_repo(repo_fullname)
        print(f"Processing {repo.full_name}...")

        try:
            contents = repo.get_contents(target_path, ref=branch)
            existing = contents.decoded_content.decode()
            sha = contents.sha
        except Exception:
            existing = None
            sha = None

        if comparator.is_same(existing, template_content):
            print("  - Skipped: Already up to date")
            continue

        if dry_run:
            print(f"  - Dry run: would update {target_path} in {repo.full_name}")
            print(generate_diff(existing, template_content, target_path))
        else:
            # Proceed with update/create commit
            if sha:
                repo.update_file(target_path, commit_message, template_content, sha, branch=branch)
            else:
                repo.create_file(target_path, commit_message, template_content, branch=branch)
            print("  - Synced successfully")
