import yaml
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class RepoConfig:
    name: str
    branch: Optional[str] = None
    message: Optional[str] = None
    path: Optional[str] = None
    vars: Dict = field(default_factory=dict)
    templates: List[str] = field(default_factory=list)

@dataclass
class Config:
    defaults: Dict
    repos: List[RepoConfig]

class ConfigLoader:
    @staticmethod
    def load(path: str) -> Config:
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        defaults = data.get("defaults", {})

        def apply_defaults(repo: Dict) -> RepoConfig:
            # Merge defaults with repo, repo values override
            merged = {
                "branch": defaults.get("branch"),
                "message": defaults.get("message"),
                "path": defaults.get("path", ".github/workflows"),
                "vars": defaults.get("vars", {}),
                "templates": defaults.get("templates", []),
                **repo,  # overrides from repo-level config
            }
            # Deep merge vars
            merged["vars"] = {**defaults.get("vars", {}), **repo.get("vars", {})}
            return RepoConfig(**merged)

        repos = [apply_defaults(r) for r in data.get("repos", [])]
        return Config(defaults=defaults, repos=repos)
