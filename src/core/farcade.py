import os
from src.providers.base import ProviderFactory
from src.state.file_state import FileStateManager
from src.template_engine.jinja_loader import JinjaTemplateEngine
from src.diff.interactive import RichDiffViewer
from src.core.sync_engine import SyncEngine
from src.utils.hash import compute_sha
from src.utils.logger import Logger

class SyncFacade:
    def __init__(self, provider_name, token, template_dir, state_file):
        self.provider = ProviderFactory.create(provider_name, token)
        self.state = FileStateManager(state_file)
        self.template = JinjaTemplateEngine(template_dir)
        self.diff = RichDiffViewer()
        self.provider_name = provider_name

    def sync(self, config, interactive: bool = True):
        engine = SyncEngine(
            provider=self.provider,
            state_mgr=self.state,
            template_eng=self.template,
            diff_viewer=self.diff,
            interactive=interactive,
            provider_name=self.provider_name,
        )
        self.state.load()
        engine.sync(config)

class DriftFacade:
    def __init__(self, provider_name, token, state_file):
        self.provider = ProviderFactory.create(provider_name, token)
        self.state = FileStateManager(state_file)
        self.diff = RichDiffViewer()
        self.provider_name = provider_name

    def detect_drift(self, reconcile: bool = False):
        self.state.load()
        drifted_files = []

        provider_repos = self.state.state.get("repos", {}).get(self.provider_name, {})

        for repo, repo_data in provider_repos.items():
            branches = repo_data.get("branches", {})
            for branch, branch_data in branches.items():
                files = branch_data.get("files", {})

                for key, file_data in files.items():
                    path = file_data.get("path")
                    expected_sha = file_data.get("sha")
                    expected_content = file_data.get("rendered")

                    remote_content = self.provider.get_file_content(repo, branch, path)

                    if remote_content is None:
                        Logger.get_logger().warning(f"{repo}:{branch} - {path} missing remotely (might be deleted)")
                        drifted_files.append((repo, branch, "create", path, expected_content, None))
                        continue

                    remote_sha = compute_sha(remote_content)

                    if remote_sha != expected_sha:
                        Logger.get_logger().info(f"Drift detected in {repo}:{branch} - {path}")
                        drifted_files.append((repo, branch, "update", path, remote_content, expected_content))

        if not drifted_files:
            Logger.get_logger().info("✅ No drift detected.")
        else:
            self.diff.display_diffs(drifted_files)
            if reconcile:
                self._reconcile(drifted_files)

    def _reconcile(self, drifted_files):
        Logger.get_logger().info("⚙️ Reconciling drift...")

        for repo, branch, action, path, _, expected_content in drifted_files:
            commit_message = f"Reconcile drift for {path}"

            sha = self.provider.sync(
                repo=repo,
                branch=branch,
                path=path,
                content=expected_content,
                commit_message=commit_message
            )

            key = os.path.basename(path) + ".j2"

            content_sha = compute_sha(expected_content)
            self.state.update_file_entry(
                repo=repo,
                branch=branch,
                key=key,
                file_path=path,
                sha=content_sha,
                rendered=expected_content,
                provider_name=self.provider_name
            )

            Logger.get_logger().info(f"✅ {repo}:{branch} - {path} reconciled")

        self.state.save()
        Logger.get_logger().info("✅ Drift reconciliation complete.")