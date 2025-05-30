from src.core.interfaces import ProviderInterface
from src.providers.github import GitHubProvider

class ProviderFactory:
    @staticmethod
    def create(name: str, token: str) -> ProviderInterface:
        if name == 'github':
            return GitHubProvider(token)
        # future: elif name == 'gitlab': return GitLabProvider(token)
        else:
            raise ValueError(f"Unknown provider {name}")
