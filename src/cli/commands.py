from src.config.loader import ConfigLoader
from src.core.farcade import SyncFacade
from src.core.init import write_example_structure
from src.utils.logger import Logger

class Command:
    def execute(self, args):
        raise NotImplementedError

class InitCommand(Command):
    def execute(self, args):
        write_example_structure(args.template_dir)
        Logger.get_logger().info(f"Template scaffold created at {args.template_dir}")

class SyncCommand(Command):
    def execute(self, args):
        config = ConfigLoader.load(args.values)
        facade = SyncFacade(
            provider_name=args.provider,
            token=args.token,
            template_dir=args.template_dir,
            state_file=args.state_file
        )
        facade.sync(config, interactive=not getattr(args, "non_interactive", False))