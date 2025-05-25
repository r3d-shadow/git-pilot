from github import Github
from core import comparator

def sync(token, repos, branch, template_content, target_path, commit_message,
         dry_run=False, state_manager=None, template_key=None):
    github = Github(token)
    dry_run_diffs = []

    for repo_fullname in repos:
        repo = github.get_repo(repo_fullname)
        print(f"Processing {repo.full_name}...")

        prev_state = state_manager.get_repo_state(repo_fullname) if state_manager else {}
        prev_files = prev_state.get("files", {})

        if template_key and template_key in prev_files:
            old_path = prev_files[template_key].get("file_path")
            if old_path and old_path != target_path:
                if dry_run:
                    print(f"  - Dry run: would remove old workflow file {old_path}")
                else:
                    try:
                        old_content = repo.get_contents(old_path, ref=branch)
                        repo.delete_file(old_path, f"ci-sync: remove old workflow file {old_path}", old_content.sha, branch=branch)
                        print(f"  - Removed old workflow file {old_path}")
                    except Exception as e:
                        print(f"  - Warning: Could not delete old workflow file {old_path}: {e}")

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
            dry_run_diffs.append((repo_fullname, action, target_path, existing, template_content))
        else:
            if sha:
                repo.update_file(target_path, commit_message, template_content, sha, branch=branch)
            else:
                repo.create_file(target_path, commit_message, template_content, branch=branch)
            print("  - Synced successfully")

            if state_manager and template_key:
                state_manager.update_repo_file(repo_fullname, template_key, target_path, sha or "new")

    return dry_run_diffs if dry_run else []