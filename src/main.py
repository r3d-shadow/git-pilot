from src.cli.parsers import ParserBuilder

def main():
    parser = ParserBuilder().with_init_command().with_sync_command().build()
    args = parser.parse_args()
    args.command.execute(args)
