import argparse
from src.cli.commands import InitCommand, SyncCommand

class ParserBuilder:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="git-piplot: sync reusable files across repos")
        self.subparsers = self.parser.add_subparsers(dest='command_name', required=True)

    def with_init_command(self):
        init_parser = self.subparsers.add_parser('init', help='Initialize template scaffold')
        init_parser.add_argument('--template-dir', required=True)
        init_parser.set_defaults(command=InitCommand())
        return self

    def with_sync_command(self):
        sync_parser = self.subparsers.add_parser('sync', help='Sync workflows')
        sync_parser.add_argument('--provider', choices=['github'], default='github')
        sync_parser.add_argument('--token', required=True)
        sync_parser.add_argument('--template-dir', required=True)
        sync_parser.add_argument('--values', required=True)
        sync_parser.add_argument('--state-file', default='.git-pilot-state.json')
        sync_parser.add_argument(
            "--non-interactive",
            action="store_true",
            help="Run sync in non-interactive mode (auto-approve all changes)"
        )
        sync_parser.set_defaults(command=SyncCommand())
        return self

    def build(self):
        return self.parser