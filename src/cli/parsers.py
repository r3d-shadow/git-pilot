import argparse
from src.cli.commands import InitCommand, SyncCommand

def build_parser():
    parser = argparse.ArgumentParser(
        description="ci-sync: sync reusable CI templates across repos"
    )
    subparsers = parser.add_subparsers(dest='command_name', required=True)

    # init command
    init_parser = subparsers.add_parser('init', help='Initialize template scaffold')
    init_parser.add_argument('--template-dir', required=True,
                             help='Directory to bootstrap template structure')
    init_parser.set_defaults(command=InitCommand())

    # sync command
    sync_parser = subparsers.add_parser('sync', help='Sync workflows')
    sync_parser.add_argument('--provider', choices=['github'], default='github',
                             help='CI provider to use')
    sync_parser.add_argument('--token', required=True, help='Access token')
    sync_parser.add_argument('--template-dir', required=True,
                             help='Directory containing Jinja2 workflow templates')
    sync_parser.add_argument('--values', required=True,
                             help='Path to values YAML with repo config')
    sync_parser.add_argument('--state-file', default='.ci-sync.json',
                             help='Path to local state file')
    sync_parser.set_defaults(command=SyncCommand())

    return parser
