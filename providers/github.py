from github import Github
from core import comparator

def sync(token, repos, branch, template_content, target_path, commit_message):
    github = Github(token)

    for repo_fullname in repos:
        repo = github.get_repo(repo_fullname)
        print(f"Processing {repo.full_name}...")
        try:
            contents = repo.get_contents(target_path)
            existing = contents.decoded_content.decode()
            sha = contents.sha
        except Exception:
            existing = None
            sha = None

        if comparator.is_same(existing, template_content):
            print("  - Skipped: Up to date")
            continue

        if sha:
            repo.update_file(target_path, commit_message, template_content, sha, branch=branch)
        else:
            repo.create_file(target_path, commit_message, template_content, branch=branch)
        print("  - Updated")
