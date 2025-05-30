import yaml
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class RepoConfig:
    name: str
    branch: str
    message: str
    path: str
    vars: Dict = field(default_factory=dict)
    templates: List[str] = field(default_factory=list)


@dataclass
class Config:
    repos: List[RepoConfig]


class ConfigLoader:
    @staticmethod
    def load(path: str) -> Config:
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        defaults = data.get("defaults", {})

        def apply_defaults(repo: Dict) -> RepoConfig:
            # Merge defaults with repo (repo overrides default)
            merged = {
                "name": repo["name"],
                "branch": repo.get("branch", defaults.get("branch")),
                "message": repo.get("message", defaults.get("message")),
                "path": repo.get("path", defaults.get("path", ".github/workflows")),
                "vars": {**defaults.get("vars", {}), **repo.get("vars", {})},
                "templates": repo.get("templates", defaults.get("templates", [])),
            }
            return RepoConfig(**merged)

        repos = [apply_defaults(r) for r in data.get("repos", [])]
        return Config(repos=repos)