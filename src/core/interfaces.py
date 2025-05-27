from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Any, Dict

class ProviderInterface(ABC):
    @abstractmethod
    def sync(
        self,
        repo: str,
        branch: str,
        path: str,
        content: str,
        commit_message: str,
        dry_run: bool,
    ) -> List[Tuple[str, str, str, Any, Any]]:
        """
        Perform create/update dry-run or real sync of a single file.
        Returns diffs when dry_run=True.
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
    def cleanup_old(self, repo: str, keys: List[str]) -> List[str]:
        """
        Remove state entries not in `keys` for the given repo.
        Returns list of file paths that should be deleted remotely.
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
