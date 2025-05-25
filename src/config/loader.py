import yaml
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class RepoConfig:
    name: str
    branch: str = 'main'
    message: str = ''
    path: str = '.github/workflows'
    vars: Dict = field(default_factory=dict)
    templates: List[str] = field(default_factory=list)

@dataclass
class Config:
    defaults: Dict
    repos: List[RepoConfig]

class ConfigLoader:
    @staticmethod
    def load(path: str) -> Config:
        data = yaml.safe_load(open(path))
        defaults = data.get('defaults', {})
        repos = [RepoConfig(**r) for r in data.get('repos', [])]
        return Config(defaults=defaults, repos=repos)
