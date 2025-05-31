from abc import ABC, abstractmethod
from typing import List, Set, Tuple, Optional, Any, Dict

class ProviderInterface(ABC):
    @abstractmethod
    def sync(
        self,
        repo: str,
        branch: str,
        path: str,
        content: str,
        commit_message: str,
    ) -> List[Tuple[str, str, str, Any, Any]]:
        """
        """
        pass

    @abstractmethod
    def delete(
        self,
        repo: str,
        branch: str,
        path: str,
        commit_message: str
    ) -> None:
        """
        Delete the given file from the repo on the given branch with commit_message.
        """
        pass

class StateInterface(ABC):
    @abstractmethod
    def load(self) -> None:
        """Load persisted state from disk or other storage."""
        pass

    @abstractmethod
    def save(self) -> None:
        """Persist current state to disk or other storage."""
        pass

    @abstractmethod
    def cleanup_old(self, repo: str, branch: str, current_keys: List[str], provider_name: str) -> List[str]:
        """
        Remove state entries not in `current_keys` for the given repo and branch under a specific provider.
        Returns list of file paths that should be deleted remotely.
        """
        pass

    @abstractmethod
    def cleanup_old_branches(self, repo: str, active_branches: Set[str], provider_name: str) -> List[Tuple[str, str]]:
        """
        Remove entries from branches that are no longer active under a specific provider.
        Returns list of (branch, file_path) tuples that should be deleted remotely.
        """
        pass

    @abstractmethod
    def update_file_entry(self, repo: str, branch: str, key: str, file_path: str, sha: str, rendered: str, provider_name: str) -> None:
        """
        Update state entry with file metadata.
        """
        pass

    @abstractmethod
    def get_file_entry(self, repo: str, branch: str, key: str, provider_name: str) -> dict:
        """
        Retrieve state metadata for a specific file entry.
        """
        pass

class TemplateInterface(ABC):
    @abstractmethod
    def list_templates(self, template_dir: str) -> List[str]:
        """Return list of template filenames (e.g. .j2 files) under template_dir."""
        pass

    @abstractmethod
    def render(self, template_path: str, vars: Dict) -> str:
        """Render a single template with the given vars, returning its content."""
        pass

class DiffViewerInterface(ABC):
    @abstractmethod
    def show(self, diffs: List[Tuple]) -> bool:
        """
        Display diffs to the user, return True to proceed or False to abort.
        """
        pass
