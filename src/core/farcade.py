from src.providers.base import ProviderFactory
from src.state.file_state import FileStateManager
from src.template_engine.jinja_loader import JinjaTemplateEngine
from src.diff.interactive import RichDiffViewer
from src.core.sync_engine import SyncEngine

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
