from core.diff import generate_diff
from github import Github
from core import comparator

def sync(token, repos, branch, template_content, target_path, commit_message, dry_run=False, state_manager=None):
    github = Github(token)
    for repo_fullname in repos:
        repo = github.get_repo(repo_fullname)
        print(f"Processing {repo.full_name}...")

        prev_state = state_manager.get_repo_state(repo_fullname) if state_manager else {}

        prev_path = prev_state.get("file_path")
        prev_sha = prev_state.get("sha")

        # Detect if the path changed (renamed workflow)
        if prev_path and prev_path != target_path:
            if dry_run:
                print(f"  - Dry run: would remove old workflow file {prev_path}")
            else:
                try:
                    old_content = repo.get_contents(prev_path, ref=branch)
                    repo.delete_file(prev_path, f"ci-sync: remove old workflow file {prev_path}", old_content.sha, branch=branch)
                    print(f"  - Removed old workflow file {prev_path}")
                except Exception as e:
                    print(f"  - Warning: Could not delete old workflow file {prev_path}: {e}")

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
            action = "update" if existing else "create"
            print(f"  - Dry run: would {action} {target_path} in {repo.full_name}")
            print(generate_diff(existing, template_content, target_path))
        else:
            if sha:
                repo.update_file(target_path, commit_message, template_content, sha, branch=branch)
            else:
                repo.create_file(target_path, commit_message, template_content, branch=branch)
            print("  - Synced successfully")

            if state_manager:
                state_manager.update_repo_state(repo_fullname, target_path, sha or "new")
                state_manager.save()